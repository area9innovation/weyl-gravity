// Independent four-prime verifier for the exact full-phase L=4 BT M4 sum.

#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <unordered_map>
#include <utility>
#include <vector>

using u64 = std::uint64_t;
using u128 = __uint128_t;

constexpr int N = 256;
constexpr int SQRT_N = 16;
constexpr int P = 1;
constexpr int MP = 3;
constexpr u64 PROP_LCM = 2822400;
constexpr std::array<u64, 4> PRIMES = {
    2305843009213693951ULL, 2305843009213693921ULL,
    2305843009213693907ULL, 2305843009213693723ULL,
};

struct Residues { std::array<u64, 4> value{}; };

u64 mul_mod(u64 a, u64 b, u64 p) {
    return static_cast<u64>((static_cast<u128>(a) * b) % p);
}

u64 pow_mod(u64 base, u64 exponent, u64 p) {
    u64 result = 1;
    while (exponent) {
        if (exponent & 1) result = mul_mod(result, base, p);
        base = mul_mod(base, base, p);
        exponent >>= 1;
    }
    return result;
}

Residues radd(const Residues &a, const Residues &b) {
    Residues result;
    for (int i = 0; i < 4; ++i) {
        result.value[i] = a.value[i] + b.value[i];
        if (result.value[i] >= PRIMES[i] || result.value[i] < a.value[i]) result.value[i] -= PRIMES[i];
    }
    return result;
}

Residues rmul(const Residues &a, const Residues &b) {
    Residues result;
    for (int i = 0; i < 4; ++i) result.value[i] = mul_mod(a.value[i], b.value[i], PRIMES[i]);
    return result;
}

Residues rint(std::int64_t value) {
    Residues result;
    for (int i = 0; i < 4; ++i) {
        if (value >= 0) result.value[i] = static_cast<u64>(value) % PRIMES[i];
        else {
            const u64 magnitude = static_cast<u64>(-(value + 1)) + 1;
            const u64 residue = magnitude % PRIMES[i];
            result.value[i] = residue ? PRIMES[i] - residue : 0;
        }
    }
    return result;
}

Residues rinverse(u64 value) {
    Residues result;
    for (int i = 0; i < 4; ++i) result.value[i] = pow_mod(value % PRIMES[i], PRIMES[i] - 2, PRIMES[i]);
    return result;
}

Residues rpow(Residues base, int exponent) {
    Residues result = rint(1);
    while (exponent) {
        if (exponent & 1) result = rmul(result, base);
        base = rmul(base, base);
        exponent >>= 1;
    }
    return result;
}

struct GI { std::int64_t re = 0; std::int64_t im = 0; };
GI gadd(GI a, GI b) { return {a.re + b.re, a.im + b.im}; }
GI gmul(GI a, GI b) { return {a.re * b.re - a.im * b.im, a.re * b.im + a.im * b.re}; }
constexpr std::array<GI, 4> PHASE = {{{1, 0}, {0, 1}, {-1, 0}, {0, -1}}};

int component(int momentum, int axis) { return (momentum >> (2 * axis)) & 3; }
int encode(const std::array<int, 4> &parts) {
    int result = 0;
    for (int axis = 0; axis < 4; ++axis) result |= (parts[axis] & 3) << (2 * axis);
    return result;
}
int addq(int left, int right) {
    std::array<int, 4> parts{};
    for (int axis = 0; axis < 4; ++axis) parts[axis] = component(left, axis) + component(right, axis);
    return encode(parts);
}
int negq(int momentum) {
    std::array<int, 4> parts{};
    for (int axis = 0; axis < 4; ++axis) parts[axis] = -component(momentum, axis);
    return encode(parts);
}
int omega(int momentum) {
    constexpr std::array<int, 4> one = {0, 2, 4, 2};
    int result = 0;
    for (int axis = 0; axis < 4; ++axis) result += one[component(momentum, axis)];
    return result;
}
bool allowed(int momentum) { return momentum != 0 && momentum != P && momentum != MP; }

u64 tuple_key(std::vector<int> values) {
    std::sort(values.begin(), values.end());
    u64 key = values.size();
    for (int value : values) key = (key << 8) | static_cast<unsigned>(value);
    return key;
}

class Kernels {
  public:
    GI b(std::vector<int> momenta) {
        const u64 key = tuple_key(momenta);
        auto found = b_cache.find(key);
        if (found != b_cache.end()) return found->second;
        GI result{};
        for (int axis = 0; axis < 4; ++axis) for (int direction : {-1, 1}) {
            GI product{1, 0};
            for (int momentum : momenta) {
                const GI phase = PHASE[(direction * component(momentum, axis)) & 3];
                product = gmul(product, {phase.re - 1, phase.im});
            }
            result = gadd(result, product);
        }
        b_cache.emplace(key, result);
        return result;
    }

    GI kernel(std::vector<int> momenta) {
        const int degree = static_cast<int>(momenta.size());
        const u64 key = tuple_key(momenta);
        auto found = kernel_cache.find(key);
        if (found != kernel_cache.end()) return found->second;
        GI result{};
        for (int i = 0; i < degree; ++i) {
            std::vector<int> rest;
            for (int j = 0; j < degree; ++j) if (j != i) rest.push_back(momenta[j]);
            result = gadd(result, gmul(b({momenta[i]}), b(rest)));
        }
        if (degree == 4) {
            constexpr int split[3][4] = {{0,1,2,3},{0,2,1,3},{0,3,1,2}};
            for (const auto &row : split)
                result = gadd(result, gmul(b({momenta[row[0]],momenta[row[1]]}), b({momenta[row[2]],momenta[row[3]]})));
        } else if (degree == 5) {
            for (int i = 0; i < 5; ++i) for (int j = i + 1; j < 5; ++j) {
                std::vector<int> rest;
                for (int k = 0; k < 5; ++k) if (k != i && k != j) rest.push_back(momenta[k]);
                result = gadd(result, gmul(b({momenta[i], momenta[j]}), b(rest)));
            }
        } else if (degree != 3) {
            throw std::runtime_error("unsupported degree");
        }
        kernel_cache.emplace(key, result);
        return result;
    }
  private:
    std::unordered_map<u64, GI> b_cache;
    std::unordered_map<u64, GI> kernel_cache;
};

struct Vertex {
    int degree;
    std::vector<int> fixed;
    std::int64_t prefactor_num;
    u64 prefactor_den;
};
struct Term {
    const char *name;
    std::vector<Vertex> vertices;
    std::int64_t coefficient_num;
    u64 coefficient_den;
    int vpower;
    bool covariance;
};

Vertex score(int degree, int sign) {
    const int q = sign > 0 ? P : MP;
    if (degree == 3) return {3, {q}, 3, 2};
    if (degree == 4) return {4, {q}, 2, SQRT_N};
    return {5, {q}, 5, 2 * N};
}
Vertex u30() { return {3, {}, 1, SQRT_N}; }
Vertex u40() { return {4, {}, 1, N}; }
Vertex f42() { return {4, {P, MP}, 6, 1}; }
Vertex q32(int sign) { const int q = sign > 0 ? P : MP; return {3, {q, q}, 3 * SQRT_N, 4}; }

std::vector<Term> make_terms() {
    return {
        {"|B|^2", {score(4,1),score(4,-1)}, 4,1,0,false},
        {"2*A.C", {score(3,1),score(5,-1)}, 8,1,0,false},
        {"-2*U30*A.B", {score(3,1),score(4,-1),u30()}, -8,1,0,false},
        {"Cov(|A|^2,U30^2/2)", {score(3,1),score(3,-1),u30(),u30()}, 2,1,0,true},
        {"Cov(|A|^2,-U40)", {score(3,1),score(3,-1),u40()}, -4,1,0,true},
        {"Cov(|A|^2,-v*F42)", {score(3,1),score(3,-1),f42()}, -4,1,1,true},
        {"Cov(|A|^2,v*|A|^2/2)", {score(3,1),score(3,-1),score(3,1),score(3,-1)}, 8,1,1,true},
        {"Cov(|A|^2,E[Q^2]/2)", {score(3,1),score(3,-1),q32(1),q32(-1)}, 32,1,2,true},
    };
}

using Signature = std::array<unsigned char, 10>;
int sig_index(int u, int v) {
    if (u > v) std::swap(u, v);
    int index = 0;
    for (int left = 0; left < 4; ++left) for (int right = left; right < 4; ++right) {
        if (left == u && right == v) return index;
        ++index;
    }
    throw std::runtime_error("signature index");
}
void pairing_rec(const std::vector<int> &slots, Signature signature, std::map<Signature,int> &out) {
    if (slots.empty()) { ++out[signature]; return; }
    const int first = slots.front();
    for (std::size_t j = 1; j < slots.size(); ++j) {
        std::vector<int> rest;
        for (std::size_t k = 1; k < slots.size(); ++k) if (k != j) rest.push_back(slots[k]);
        Signature changed = signature;
        ++changed[sig_index(first, slots[j])];
        pairing_rec(rest, changed, out);
    }
}
std::map<Signature,int> topologies(const Term &term) {
    std::vector<int> slots;
    for (int vertex = 0; vertex < static_cast<int>(term.vertices.size()); ++vertex)
        for (int leg = term.vertices[vertex].fixed.size(); leg < term.vertices[vertex].degree; ++leg) slots.push_back(vertex);
    std::map<Signature,int> result;
    pairing_rec(slots, Signature{}, result);
    if (term.covariance) {
        for (auto it = result.begin(); it != result.end();) {
            bool crossing = false;
            for (int u = 0; u < 2; ++u) for (int v = 2; v < static_cast<int>(term.vertices.size()); ++v)
                crossing = crossing || it->first[sig_index(u,v)] != 0;
            if (!crossing) it = result.erase(it); else ++it;
        }
    }
    return result;
}
std::vector<std::pair<int,int>> edges_from(const Signature &signature, int vertices) {
    std::vector<std::pair<int,int>> edges;
    for (int u=0;u<vertices;++u) for(int v=u;v<vertices;++v)
        for(int count=signature[sig_index(u,v)];count;--count) edges.push_back({u,v});
    return edges;
}

struct DSU {
    std::array<int,4> parent{0,1,2,3};
    int find(int x) { return parent[x]==x ? x : parent[x]=find(parent[x]); }
    bool join(int a,int b) { a=find(a);b=find(b);if(a==b)return false;parent[b]=a;return true; }
};

class Evaluator {
  public:
    Evaluator(const Term &term_, const Signature &signature)
        : term(term_), edges(edges_from(signature, term_.vertices.size())), vertex_count(term_.vertices.size()) {
        vmom.resize(vertex_count);
        sources.assign(vertex_count,0);
        for (int v=0;v<vertex_count;++v) for(int q:term.vertices[v].fixed) {
            vmom[v].push_back(q); sources[v]=addq(sources[v],q);
        }
    }
    Residues run() {
        DSU dsu;
        std::vector<int> tree,chords;
        for(int i=0;i<static_cast<int>(edges.size());++i) {
            auto [u,v]=edges[i];
            if(u==v||!dsu.join(u,v)) chords.push_back(i); else tree.push_back(i);
        }
        std::array<int,4> component_source{};
        for(int v=0;v<vertex_count;++v) component_source[dsu.find(v)]=addq(component_source[dsu.find(v)],sources[v]);
        for(int v=0;v<vertex_count;++v) if(dsu.find(v)==v&&component_source[v]!=0) return {};
        if(chords.size()>3) throw std::runtime_error("more than three loops");
        std::vector<std::vector<std::pair<int,int>>> adjacency(vertex_count);
        for(int edge:tree) { auto [u,v]=edges[edge];adjacency[u].push_back({v,edge});adjacency[v].push_back({u,edge}); }
        std::vector<int> parent(vertex_count,-1),parent_edge(vertex_count,-1),order;
        for(int root=0;root<vertex_count;++root) if(parent[root]==-1) {
            parent[root]=root;std::vector<int> stack{root};
            while(!stack.empty()) { int v=stack.back();stack.pop_back();order.push_back(v);
                for(auto [next,edge]:adjacency[v]) if(parent[next]==-1) {parent[next]=v;parent_edge[next]=edge;stack.push_back(next);} }
        }
        std::vector<int> edge_momentum(edges.size());
        enumerate(0,chords,parent,parent_edge,order,edge_momentum);
        int kernel_den=1;
        for(const auto &item:term.vertices) kernel_den*=item.degree==3?6:item.degree==4?24:120;
        return rmul(total,rmul(rinverse(kernel_den),rpow(rinverse(PROP_LCM),edges.size())));
    }
  private:
    const Term &term;
    std::vector<std::pair<int,int>> edges;
    int vertex_count;
    std::vector<std::vector<int>> vmom;
    std::vector<int> sources;
    Residues total{};
    Kernels kernels;

    void enumerate(int at,const std::vector<int>&chords,const std::vector<int>&parent,
                   const std::vector<int>&parent_edge,const std::vector<int>&order,std::vector<int>&values) {
        if(at!=static_cast<int>(chords.size())) {
            const int edge=chords[at];
            for(int q=1;q<N;++q) if(allowed(q)) { values[edge]=q;enumerate(at+1,chords,parent,parent_edge,order,values); }
            return;
        }
        std::vector<int> balances=sources;
        for(int edge:chords) {auto [u,v]=edges[edge];int q=values[edge];if(u!=v){balances[u]=addq(balances[u],q);balances[v]=addq(balances[v],negq(q));}}
        for(auto it=order.rbegin();it!=order.rend();++it) {
            int v=*it;
            if(parent[v]==v) {if(balances[v]!=0)return;continue;}
            int edge=parent_edge[v];auto [u,_]=edges[edge];int endpoint=negq(balances[v]);int q=v==u?endpoint:negq(endpoint);
            if (!allowed(q)) return;
            values[edge] = q;
            balances[parent[v]] = addq(balances[parent[v]], balances[v]);
        }
        evaluate(values);
    }
    void evaluate(const std::vector<int>&values) {
        std::vector<int> old(vertex_count);
        for(int v=0;v<vertex_count;++v)old[v]=vmom[v].size();
        Residues propagator=rint(1);
        for(int i=0;i<static_cast<int>(edges.size());++i) {auto [u,v]=edges[i];int q=values[i];
            vmom[u].push_back(q);vmom[v].push_back(negq(q));propagator=rmul(propagator,rint(PROP_LCM/(omega(q)*omega(q))));}
        GI product{1,0};
        for(int v=0;v<vertex_count;++v) {int sum=0;for(int q:vmom[v])sum=addq(sum,q);if(sum)throw std::runtime_error("momentum");
            product=gmul(product,kernels.kernel(vmom[v]));}
        if(product.im)throw std::runtime_error("non-real");
        total=radd(total,rmul(propagator,rint(product.re)));
        for(int v=0;v<vertex_count;++v)vmom[v].resize(old[v]);
    }
};

Residues evaluate_term(const Term &term) {
    Residues result{};
    for(const auto &[signature,multiplicity]:topologies(term)) {
        Evaluator evaluator(term,signature);
        result=radd(result,rmul(rint(multiplicity),evaluator.run()));
    }
    Residues outer=rmul(rint(term.coefficient_num),rinverse(term.coefficient_den));
    outer=rmul(outer,rpow(rinverse(512),term.vpower));
    for(const auto &item:term.vertices) outer=rmul(outer,rmul(rint(item.prefactor_num),rinverse(item.prefactor_den)));
    return rmul(result,outer);
}

int main() {
    try {
        const auto terms=make_terms();
        std::vector<Residues> rows;
        Residues total{};
        for(const auto &term:terms){Residues value=evaluate_term(term);rows.push_back(value);total=radd(total,value);}
        std::cout<<"{\"primes\":[";
        for(int i=0;i<4;++i){if(i)std::cout<<',';std::cout<<PRIMES[i];}
        std::cout<<"],\"terms\":[";
        for(std::size_t row=0;row<rows.size();++row){if(row)std::cout<<',';std::cout<<'[';
            for(int i=0;i<4;++i){if(i)std::cout<<',';std::cout<<rows[row].value[i];}std::cout<<']';}
        std::cout<<"],\"M4\":[";
        for(int i=0;i<4;++i){if(i)std::cout<<',';std::cout<<total.value[i];}
        std::cout<<"]}\n";
        return 0;
    } catch(const std::exception &error) {std::cerr<<error.what()<<'\n';return 1;}
}
