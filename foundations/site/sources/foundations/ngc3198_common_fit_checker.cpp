#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Point { double r, observed, error, sn, sl, gn, gl, global_l, global_q; };

static std::string slurp(const std::string& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("cannot open " + path);
    return std::string((std::istreambuf_iterator<char>(input)), std::istreambuf_iterator<char>());
}

static double number_after(const std::string& text, const std::string& key) {
    const std::string token = "\"" + key + "\"";
    auto pos = text.find(token);
    if (pos == std::string::npos) throw std::runtime_error("missing key " + key);
    pos = text.find(':', pos + token.size());
    pos = text.find_first_of("-+.0123456789", pos + 1);
    return std::stod(text.substr(pos));
}

static std::vector<Point> load_points(const std::string& root) {
    const auto parameters = slurp(root + "/foundations/data/mannheim-ngc3198-parameters-v1.json");
    const double beta = number_after(parameters, "beta_star_cm");
    const double gamma_star = number_after(parameters, "gamma_star_per_cm");
    const double gamma0 = number_after(parameters, "gamma_0_per_cm");
    const double kappa = number_after(parameters, "kappa_per_cm2");
    const double light = number_after(parameters, "speed_of_light_cm_per_s");
    const double kpc = number_after(parameters, "kpc_cm");
    const double stars = number_after(parameters, "stellar_disk_mass_1e10_solar") * 1e10;
    const double gas = number_after(parameters, "hi_mass_1e10_solar") * 1e10 * 1.4;
    const double star_scale = number_after(parameters, "stellar_scale_length_kpc") * kpc;
    const double gas_scale = 4.0 * star_scale;
    std::ifstream input(root + "/foundations/data/ngc3198-sparc-mass-model-v1.tsv");
    std::vector<Point> points;
    std::string line;
    while (std::getline(input, line)) {
        if (line.empty() || line[0] == '#') continue;
        std::istringstream row(line);
        std::string galaxy;
        double distance, radius, observed, error, unused;
        row >> galaxy >> distance >> radius >> observed >> error;
        for (int i = 0; i < 5; ++i) row >> unused;
        const double r = radius * 14.1 / distance;
        if (galaxy != "NGC3198" || r > 38.6) continue;
        const double radius_cm = r * kpc;
        auto disk = [&](double count, double scale) {
            const double y = radius_cm / (2.0 * scale);
            const double i0 = std::cyl_bessel_i(0.0, y), i1 = std::cyl_bessel_i(1.0, y);
            const double k0 = std::cyl_bessel_k(0.0, y), k1 = std::cyl_bessel_k(1.0, y);
            const double n = count * beta * light * light * radius_cm * radius_cm * (i0*k0-i1*k1) / (2.0*scale*scale*scale) / 1e10;
            const double l = count * gamma_star * light * light * radius_cm * radius_cm * i1*k1 / (2.0*scale) / 1e10;
            return std::pair<double,double>{n,l};
        };
        const auto s = disk(stars, star_scale), g = disk(gas, gas_scale);
        points.push_back({r, observed, error, s.first, s.second, g.first, g.second,
            gamma0*light*light*radius_cm/2.0/1e10, -kappa*light*light*radius_cm*radius_cm/1e10});
    }
    if (points.size() != 39) throw std::runtime_error("point-count closure failed");
    return points;
}

static double nfw_v2(double r, double v200, double c) {
    const double x = r / (100.0*v200/70.0);
    return v200*v200 * (std::log1p(c*x)-c*x/(1.0+c*x)) / (x*(std::log1p(c)-c/(1.0+c)));
}

static double score(const std::vector<Point>& points, int family, double q, double v200=0.0, double c=0.0) {
    double result = 0.0;
    for (const auto& p : points) {
        double v2 = q*p.sn + p.gn;
        if (family == 1) v2 += nfw_v2(p.r, v200, c);
        if (family == 2) v2 = q*(p.sn+p.sl)+p.gn+p.gl+p.global_l+p.global_q;
        if (!(v2 > 0.0)) return INFINITY;
        const double z = (std::sqrt(v2)-p.observed)/p.error;
        result += z*z;
    }
    return result;
}

template<class F> static double golden(F function, double lo, double hi) {
    const double ratio = (std::sqrt(5.0)-1.0)/2.0;
    double c = hi-ratio*(hi-lo), d = lo+ratio*(hi-lo), fc=function(c), fd=function(d);
    for (int i=0; i<110; ++i) {
        if (fc <= fd) { hi=d; d=c; fd=fc; c=hi-ratio*(hi-lo); fc=function(c); }
        else { lo=c; c=d; fc=fd; d=lo+ratio*(hi-lo); fd=function(d); }
    }
    return (lo+hi)/2.0;
}

static std::array<double,4> nelder_mead(const std::vector<Point>& points, double q0, double v0, double c0) {
    using V = std::array<double,3>;
    struct Node { V x; double f; };
    auto objective = [&](const V& x) {
        if (x[0]<0.1 || x[0]>3.0 || x[1]<std::log(20.0) || x[1]>std::log(500.0) || x[2]<0.0 || x[2]>std::log(40.0)) return std::numeric_limits<double>::infinity();
        return score(points,1,x[0],std::exp(x[1]),std::exp(x[2]));
    };
    std::array<Node,4> simplex{{{{q0,std::log(v0),std::log(c0)},0},{{q0+0.08,std::log(v0),std::log(c0)},0},{{q0,std::log(v0)+0.08,std::log(c0)},0},{{q0,std::log(v0),std::log(c0)+0.08},0}}};
    for (auto& n : simplex) n.f=objective(n.x);
    for (int iteration=0; iteration<4000; ++iteration) {
        std::sort(simplex.begin(),simplex.end(),[](const Node&a,const Node&b){return a.f<b.f;});
        V centroid{};
        for(int i=0;i<3;++i) for(int j=0;j<3;++j) centroid[j]+=simplex[i].x[j]/3.0;
        auto combine=[&](double factor){V x{};for(int j=0;j<3;++j)x[j]=centroid[j]+factor*(centroid[j]-simplex[3].x[j]);return Node{x,objective(x)};};
        Node reflected=combine(1.0);
        if(reflected.f<simplex[0].f){Node expanded=combine(2.0);simplex[3]=(expanded.f<reflected.f?expanded:reflected);}
        else if(reflected.f<simplex[2].f) simplex[3]=reflected;
        else {
            Node contracted=combine(-0.5);
            if(contracted.f<simplex[3].f) simplex[3]=contracted;
            else for(int i=1;i<4;++i){for(int j=0;j<3;++j)simplex[i].x[j]=0.5*(simplex[i].x[j]+simplex[0].x[j]);simplex[i].f=objective(simplex[i].x);}
        }
        double span=0.0; for(int i=1;i<4;++i)for(int j=0;j<3;++j)span=std::max(span,std::abs(simplex[i].x[j]-simplex[0].x[j]));
        if(span<1e-12) break;
    }
    std::sort(simplex.begin(),simplex.end(),[](const Node&a,const Node&b){return a.f<b.f;});
    return {simplex[0].f,simplex[0].x[0],std::exp(simplex[0].x[1]),std::exp(simplex[0].x[2])};
}

int main(int argc, char** argv) {
    if (argc != 2) { std::cerr << "usage: checker REPOSITORY_ROOT\n"; return 2; }
    try {
        const auto points = load_points(argv[1]);
        const double qb = golden([&](double q){ return score(points,0,q); },0.1,3.0);
        const double qm = golden([&](double q){ return score(points,2,q); },0.1,3.0);
        // Independent Nelder--Mead searches from dispersed starts, unlike the producer's nested grid.
        double best_score=INFINITY, best_q=0.0, best_v=0.0, best_c=0.0;
        for (double start_v : {45.0, 90.0, 150.0, 300.0}) for (double start_c : {2.0, 6.0, 15.0, 30.0}) {
            const auto fit=nelder_mead(points,1.0,start_v,start_c);
            if (fit[0] < best_score) { best_score=fit[0]; best_q=fit[1]; best_v=fit[2]; best_c=fit[3]; }
        }
        std::cout << std::setprecision(17)
          << "{\"NEWTONIAN_BARYONS_ONLY\":{\"q_star\":" << qb << ",\"chi_squared\":" << score(points,0,qb) << "},"
          << "\"GR_NFW_DARK_HALO\":{\"q_star\":" << best_q << ",\"V200_km_s\":" << best_v << ",\"concentration_c200\":" << best_c << ",\"chi_squared\":" << best_score << "},"
          << "\"MANNHEIM_CONFORMAL_GRAVITY\":{\"q_star\":" << qm << ",\"chi_squared\":" << score(points,2,qm) << "}}\n";
    } catch (const std::exception& error) { std::cerr << error.what() << "\n"; return 1; }
}
