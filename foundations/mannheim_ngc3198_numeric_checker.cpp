#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
constexpr double beta_star = 1.48e5;
constexpr double gamma_star = 5.42e-41;
constexpr double gamma_0 = 3.06e-30;
constexpr double kappa = 9.54e-54;
constexpr double light_speed = 2.99792458e10;
constexpr double kpc_cm = 3.0856775814913673e21;
constexpr double adopted_distance = 14.1;
constexpr double stellar_count = 3.644e10;
constexpr double gas_count = 1.4 * 1.06e10;
constexpr double stellar_scale = 4.0 * kpc_cm;
constexpr double gas_scale = 16.0 * kpc_cm;
constexpr double last_radius = 38.6;

double disk_v2(double radius, double count, double scale) {
  const double y = radius / (2.0 * scale);
  const double i0 = std::cyl_bessel_i(0.0, y);
  const double i1 = std::cyl_bessel_i(1.0, y);
  const double k0 = std::cyl_bessel_k(0.0, y);
  const double k1 = std::cyl_bessel_k(1.0, y);
  const double newtonian = count * beta_star * light_speed * light_speed * radius * radius
      * (i0 * k0 - i1 * k1) / (2.0 * scale * scale * scale);
  const double linear = count * gamma_star * light_speed * light_speed * radius * radius
      * i1 * k1 / (2.0 * scale);
  return newtonian + linear;
}

double velocity(double radius_kpc) {
  const double radius = radius_kpc * kpc_cm;
  const double total = disk_v2(radius, stellar_count, stellar_scale)
      + disk_v2(radius, gas_count, gas_scale)
      + gamma_0 * light_speed * light_speed * radius / 2.0
      - kappa * light_speed * light_speed * radius * radius;
  if (!(total > 0.0)) throw std::runtime_error("non-positive circular velocity squared");
  return std::sqrt(total) / 1e5;
}
}

int main(int argc, char** argv) {
  if (argc != 2) {
    std::cerr << "usage: checker <SPARC extract>\n";
    return 2;
  }
  std::ifstream input(argv[1]);
  if (!input) {
    std::cerr << "cannot open SPARC extract\n";
    return 2;
  }
  std::string line;
  int source_points = 0;
  int selected_points = 0;
  double squared_sum = 0.0;
  double chi_squared = 0.0;
  double maximum = 0.0;
  while (std::getline(input, line)) {
    if (line.empty() || line[0] == '#') continue;
    std::istringstream row(line);
    std::string id;
    double distance, radius, observed, error, gas, disk, bulge, sb_disk, sb_bulge;
    if (!(row >> id >> distance >> radius >> observed >> error >> gas >> disk >> bulge >> sb_disk >> sb_bulge) || id != "NGC3198") {
      std::cerr << "bad SPARC row\n";
      return 2;
    }
    ++source_points;
    const double rescaled_radius = radius * adopted_distance / distance;
    if (rescaled_radius > last_radius) continue;
    const double residual = velocity(rescaled_radius) - observed;
    squared_sum += residual * residual;
    chi_squared += residual * residual / (error * error);
    maximum = std::max(maximum, std::abs(residual));
    ++selected_points;
  }
  if (source_points != 43 || selected_points != 39) {
    std::cerr << "point-count closure failed\n";
    return 2;
  }
  const double endpoint_velocity = velocity(last_radius);
  const double observed_acceleration = 2.09e-30;
  const double observed_endpoint_velocity = std::sqrt(observed_acceleration * light_speed * light_speed * last_radius * kpc_cm) / 1e5;
  std::cout << std::setprecision(17)
            << "source_points=" << source_points << "\n"
            << "selected_points=" << selected_points << "\n"
            << "endpoint_velocity_km_s=" << endpoint_velocity << "\n"
            << "observed_endpoint_velocity_km_s=" << observed_endpoint_velocity << "\n"
            << "endpoint_relative_residual=" << std::abs(endpoint_velocity - observed_endpoint_velocity) / observed_endpoint_velocity << "\n"
            << "rms_residual_km_s=" << std::sqrt(squared_sum / selected_points) << "\n"
            << "maximum_absolute_residual_km_s=" << maximum << "\n"
            << "chi_squared=" << chi_squared << "\n"
            << "reduced_chi_squared=" << chi_squared / selected_points << "\n";
  return 0;
}
