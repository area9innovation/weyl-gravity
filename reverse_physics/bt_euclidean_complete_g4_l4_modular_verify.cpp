// Independent modular verifier for the exact L=4 connected BT g^4 sum.
//
// This implementation does not import the Python topology ledger.  It
// independently enumerates labeled Wick pairings, groups their multigraphs,
// expands C=C0-v h h, solves the Z_4^4 momentum-flow equations, and emits the
// four-prime residues of every term.  The Python verifier combines these
// residues with a rigorous integer bound to turn agreement into an exact
// rational equality rather than a probabilistic modular check.

#include <algorithm>
#include <array>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <map>
#include <numeric>
#include <stdexcept>
#include <unordered_map>
#include <utility>
#include <vector>

using u64 = std::uint64_t;
using u128 = __uint128_t;

constexpr int L = 4;
constexpr int N = 256;
constexpr int SQRT_N = 16;
constexpr int P = 1;
constexpr int MP = 3;
constexpr int OMEGA_P = 2;
constexpr u64 PROP_LCM = 2822400;
constexpr std::array<u64, 4> PRIMES = {
    2305843009213693951ULL,
    2305843009213693921ULL,
    2305843009213693907ULL,
    2305843009213693723ULL,
};

struct Residues {
    std::array<u64, 4> value{};
};

u64 add_mod(u64 a, u64 b, u64 p) {
    u64 result = a + b;
    if (result >= p || result < a) result -= p;
    return result;
}

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
    for (int i = 0; i < 4; ++i) result.value[i] = add_mod(a.value[i], b.value[i], PRIMES[i]);
    return result;
}

Residues rneg(const Residues &a) {
    Residues result;
    for (int i = 0; i < 4; ++i) result.value[i] = a.value[i] ? PRIMES[i] - a.value[i] : 0;
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

struct GI {
    std::int64_t re = 0;
    std::int64_t im = 0;
};

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
        for (int axis = 0; axis < 4; ++axis) {
            for (int direction : {-1, 1}) {
                GI product{1, 0};
                for (int momentum : momenta) {
                    GI phase = PHASE[(direction * component(momentum, axis)) & 3];
                    product = gmul(product, {phase.re - 1, phase.im});
                }
                result = gadd(result, product);
            }
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
        if (degree == 3 || degree == 4 || degree == 5) {
            for (int i = 0; i < degree; ++i) {
                std::vector<int> rest;
                for (int j = 0; j < degree; ++j) if (j != i) rest.push_back(momenta[j]);
                result = gadd(result, gmul(b({momenta[i]}), b(rest)));
            }
        }
        if (degree == 4) {
            constexpr int split[3][4] = {{0, 1, 2, 3}, {0, 2, 1, 3}, {0, 3, 1, 2}};
            for (auto &row : split) result = gadd(result, gmul(b({momenta[row[0]], momenta[row[1]]}), b({momenta[row[2]], momenta[row[3]]})));
        } else if (degree == 5) {
            for (int i = 0; i < 5; ++i) for (int j = i + 1; j < 5; ++j) {
                std::vector<int> right;
                for (int k = 0; k < 5; ++k) if (k != i && k != j) right.push_back(momenta[k]);
                result = gadd(result, gmul(b({momenta[i], momenta[j]}), b(right)));
            }
        } else if (degree != 3 && degree != 4) {
            throw std::runtime_error("unsupported kernel degree");
        }
        kernel_cache.emplace(key, result);
        return result;
    }

  private:
    std::unordered_map<u64, GI> b_cache;
    std::unordered_map<u64, GI> kernel_cache;
};

struct Atom { int degree; int hlegs; };
struct Term {
    const char *name;
    std::vector<Atom> atoms;
    std::int64_t coefficient_num;
    u64 coefficient_den;
    int vpower;
    bool covariance;
};

const std::vector<Term> TERMS = {
    {"U41^2", {{4,1},{4,1}}, 1,1,0,false},
    {"2*U31*U51", {{3,1},{5,1}}, 2,1,0,false},
    {"-2*U31*U41*U30", {{3,1},{4,1},{3,0}}, -2,1,0,false},
    {"-2*v*U31*U41*U32", {{3,1},{4,1},{3,2}}, -2,1,1,false},
    {"Cov(U31^2,U30^2)", {{3,1},{3,1},{3,0},{3,0}}, 1,2,0,true},
    {"Cov(U31^2,U30*U32)", {{3,1},{3,1},{3,0},{3,2}}, 1,1,1,true},
    {"Cov(U31^2,U32^2)", {{3,1},{3,1},{3,2},{3,2}}, 3,2,2,true},
    {"Cov(U31^2,-U40)", {{3,1},{3,1},{4,0}}, -1,1,0,true},
    {"Cov(U31^2,-v*U42)", {{3,1},{3,1},{4,2}}, -1,1,1,true},
    {"Cov(U31^2,-3*v^2*U44)", {{3,1},{3,1},{4,4}}, -3,1,2,true},
    {"Cov(U31^2,v*U31^2/2)", {{3,1},{3,1},{3,1},{3,1}}, 1,2,1,true},
    {"Cov(U31^2,3*v^2*U31*U33)", {{3,1},{3,1},{3,1},{3,3}}, 3,1,2,true},
    {"Cov(U31^2,15*v^3*U33^2/2)", {{3,1},{3,1},{3,3},{3,3}}, 15,2,3,true},
};

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

void pairing_rec(const std::vector<int> &slots, Signature signature, std::map<Signature, int> &out) {
    if (slots.empty()) {
        ++out[signature];
        return;
    }
    const int first = slots.front();
    for (std::size_t j = 1; j < slots.size(); ++j) {
        std::vector<int> rest;
        for (std::size_t k = 1; k < slots.size(); ++k) if (k != j) rest.push_back(slots[k]);
        Signature changed = signature;
        ++changed[sig_index(first, slots[j])];
        pairing_rec(rest, changed, out);
    }
}

std::map<Signature, int> topologies(const Term &term) {
    std::vector<int> slots;
    for (int vertex = 0; vertex < static_cast<int>(term.atoms.size()); ++vertex)
        for (int leg = 0; leg < term.atoms[vertex].degree - term.atoms[vertex].hlegs; ++leg)
            slots.push_back(vertex);
    std::map<Signature, int> result;
    pairing_rec(slots, Signature{}, result);
    if (term.covariance) {
        for (auto it = result.begin(); it != result.end();) {
            bool crossing = false;
            for (int u = 0; u < 2; ++u) for (int v = 2; v < static_cast<int>(term.atoms.size()); ++v)
                crossing = crossing || it->first[sig_index(u, v)] != 0;
            if (!crossing) it = result.erase(it); else ++it;
        }
    }
    return result;
}

std::vector<std::pair<int,int>> edges_from(const Signature &signature, int vertices) {
    std::vector<std::pair<int,int>> edges;
    for (int u = 0; u < vertices; ++u) for (int v = u; v < vertices; ++v)
        for (int count = signature[sig_index(u,v)]; count; --count) edges.push_back({u,v});
    return edges;
}

struct DSU {
    std::array<int,4> parent{0,1,2,3};
    int find(int x) { return parent[x] == x ? x : parent[x] = find(parent[x]); }
    bool join(int a, int b) { a=find(a); b=find(b); if(a==b) return false; parent[b]=a; return true; }
};

class TopologyEvaluator {
  public:
    TopologyEvaluator(const Term &term_, const Signature &signature_)
        : term(term_), edges(edges_from(signature_, static_cast<int>(term_.atoms.size()))), vertex_count(term_.atoms.size()) {
        vmom.resize(vertex_count);
        sources.assign(vertex_count, 0);
    }

    Residues run() {
        external_vertex(0);
        const int kernel_den = [&] {
            int value = 1;
            for (auto atom : term.atoms) value *= atom.degree == 3 ? 6 : atom.degree == 4 ? 24 : 120;
            return value;
        }();
        Residues scale = rmul(rinverse(kernel_den), rpow(rinverse(PROP_LCM), edges.size()));
        return rmul(total, scale);
    }

  private:
    const Term &term;
    std::vector<std::pair<int,int>> edges;
    int vertex_count;
    std::vector<std::vector<int>> vmom;
    std::vector<int> sources;
    Residues total{};
    Kernels kernels;

    void external_vertex(int vertex) {
        if (vertex == vertex_count) {
            for (unsigned mask = 0; mask < (1u << edges.size()); ++mask) rank_edge(0, mask);
            return;
        }
        external_leg(vertex, 0);
    }

    void external_leg(int vertex, int leg) {
        if (leg == term.atoms[vertex].hlegs) {
            external_vertex(vertex + 1);
            return;
        }
        for (int momentum : {P, MP}) {
            vmom[vertex].push_back(momentum);
            sources[vertex] = addq(sources[vertex], momentum);
            external_leg(vertex, leg + 1);
            sources[vertex] = addq(sources[vertex], negq(momentum));
            vmom[vertex].pop_back();
        }
    }

    void rank_edge(int edge_index, unsigned mask) {
        if (edge_index == static_cast<int>(edges.size())) {
            solve_bulk(mask);
            return;
        }
        if (!(mask & (1u << edge_index))) {
            rank_edge(edge_index + 1, mask);
            return;
        }
        auto [u,v] = edges[edge_index];
        for (int left : {P, MP}) for (int right : {P, MP}) {
            vmom[u].push_back(left); vmom[v].push_back(right);
            sources[u] = addq(sources[u], left); sources[v] = addq(sources[v], right);
            rank_edge(edge_index + 1, mask);
            sources[u] = addq(sources[u], negq(left)); sources[v] = addq(sources[v], negq(right));
            vmom[v].pop_back(); vmom[u].pop_back();
        }
    }

    void solve_bulk(unsigned rank_mask) {
        std::vector<int> bulk_global;
        std::vector<std::pair<int,int>> bulk;
        for (int i = 0; i < static_cast<int>(edges.size()); ++i) if (!(rank_mask & (1u << i))) {
            bulk_global.push_back(i); bulk.push_back(edges[i]);
        }
        DSU dsu;
        std::vector<int> tree, chords;
        for (int i = 0; i < static_cast<int>(bulk.size()); ++i) {
            auto [u,v] = bulk[i];
            if (u == v || !dsu.join(u,v)) chords.push_back(i); else tree.push_back(i);
        }
        std::array<int,4> component_source{};
        for (int v = 0; v < vertex_count; ++v) component_source[dsu.find(v)] = addq(component_source[dsu.find(v)], sources[v]);
        for (int v = 0; v < vertex_count; ++v) if (dsu.find(v) == v && component_source[v] != 0) return;
        if (chords.size() > 2) throw std::runtime_error("a viable conditioned graph has more than two free loops");

        std::vector<std::vector<std::pair<int,int>>> adjacency(vertex_count);
        for (int index : tree) {
            auto [u,v] = bulk[index];
            adjacency[u].push_back({v,index}); adjacency[v].push_back({u,index});
        }
        std::vector<int> parent(vertex_count,-1), parent_edge(vertex_count,-1), order;
        for (int root = 0; root < vertex_count; ++root) if (parent[root] == -1) {
            parent[root] = root;
            std::vector<int> stack{root};
            while (!stack.empty()) {
                int vertex = stack.back(); stack.pop_back(); order.push_back(vertex);
                for (auto [next,index] : adjacency[vertex]) if (parent[next] == -1) {
                    parent[next]=vertex; parent_edge[next]=index; stack.push_back(next);
                }
            }
        }
        std::vector<int> edge_momentum(bulk.size(),0);
        enumerate_chords(0, chords, bulk, tree, parent, parent_edge, order, edge_momentum, rank_mask);
    }

    void enumerate_chords(int at, const std::vector<int> &chords,
                          const std::vector<std::pair<int,int>> &bulk,
                          const std::vector<int> &tree, const std::vector<int> &parent,
                          const std::vector<int> &parent_edge, const std::vector<int> &order,
                          std::vector<int> &edge_momentum, unsigned rank_mask) {
        if (at != static_cast<int>(chords.size())) {
            const int edge = chords[at];
            for (int q = 1; q < N; ++q) {
                edge_momentum[edge] = q;
                enumerate_chords(at+1,chords,bulk,tree,parent,parent_edge,order,edge_momentum,rank_mask);
            }
            return;
        }
        std::vector<int> balances = sources;
        for (int edge : chords) {
            auto [u,v] = bulk[edge]; int q=edge_momentum[edge];
            if (u != v) { balances[u]=addq(balances[u],q); balances[v]=addq(balances[v],negq(q)); }
        }
        bool valid = true;
        for (auto it=order.rbegin(); it!=order.rend(); ++it) {
            int vertex=*it;
            if (parent[vertex] == vertex) { if (balances[vertex] != 0) valid=false; continue; }
            int edge=parent_edge[vertex]; auto [u,v]=bulk[edge];
            int endpoint=negq(balances[vertex]);
            int q = vertex == u ? endpoint : negq(endpoint);
            if (q == 0) { valid=false; break; }
            edge_momentum[edge]=q;
            balances[parent[vertex]]=addq(balances[parent[vertex]],balances[vertex]);
        }
        if (valid) evaluate_solution(bulk, edge_momentum, rank_mask);
    }

    void evaluate_solution(const std::vector<std::pair<int,int>> &bulk,
                           const std::vector<int> &edge_momentum, unsigned rank_mask) {
        std::vector<int> old_counts(vertex_count);
        for (int v=0;v<vertex_count;++v) old_counts[v]=vmom[v].size();
        Residues propagator = rint(1);
        for (int i=0;i<static_cast<int>(bulk.size());++i) {
            auto [u,v]=bulk[i]; int q=edge_momentum[i];
            vmom[u].push_back(q); vmom[v].push_back(negq(q));
            propagator=rmul(propagator,rint(PROP_LCM/(omega(q)*omega(q))));
        }
        int rank_count=0;
        for (int i=0;i<static_cast<int>(edges.size());++i) if(rank_mask&(1u<<i)) ++rank_count;
        for(int i=0;i<rank_count;++i) propagator=rmul(propagator,rint(-static_cast<std::int64_t>(PROP_LCM/(2*OMEGA_P*OMEGA_P))));
        GI product{1,0};
        for(int v=0;v<vertex_count;++v) {
            if(static_cast<int>(vmom[v].size())!=term.atoms[v].degree) throw std::runtime_error("leg count");
            int sum=0; for(int q:vmom[v]) sum=addq(sum,q);
            if(sum!=0) throw std::runtime_error("momentum conservation");
            product=gmul(product,kernels.kernel(vmom[v]));
        }
        if(product.im!=0) throw std::runtime_error("non-real topology");
        total=radd(total,rmul(propagator,rint(product.re)));
        for(int v=0;v<vertex_count;++v) vmom[v].resize(old_counts[v]);
    }
};

Residues atom_prefactor(Atom atom) {
    int d=atom.degree-atom.hlegs;
    std::int64_t numerator=1, denominator=1;
    auto choose=[](int n,int r){ int x=1; for(int i=1;i<=r;++i)x=x*(n-r+i)/i; return x; };
    numerator*=choose(atom.degree,atom.hlegs);
    denominator*=1LL<<atom.hlegs;
    if(2-d>=0) for(int i=0;i<2-d;++i) numerator*=SQRT_N;
    else for(int i=0;i<d-2;++i) denominator*=SQRT_N;
    return rmul(rint(numerator),rinverse(denominator));
}

Residues evaluate_term(const Term &term) {
    for(auto atom:term.atoms) if(atom.degree==3 && atom.hlegs==3) return Residues{};
    Residues result{};
    for(auto &[signature,multiplicity]:topologies(term)) {
        TopologyEvaluator evaluator(term,signature);
        result=radd(result,rmul(rint(multiplicity),evaluator.run()));
    }
    Residues outer=rmul(rint(term.coefficient_num),rinverse(term.coefficient_den));
    outer=rmul(outer,rpow(rinverse(512),term.vpower));
    for(auto atom:term.atoms) outer=rmul(outer,atom_prefactor(atom));
    return rmul(result,outer);
}

int main() {
    try {
        std::vector<Residues> rows;
        Residues total{};
        for(const auto &term:TERMS) {
            Residues value=evaluate_term(term); rows.push_back(value); total=radd(total,value);
        }
        std::cout << "{\"primes\":[";
        for(int i=0;i<4;++i){
            if(i) std::cout<<',';
            std::cout<<PRIMES[i];
        }
        std::cout << "],\"terms\":[";
        for(std::size_t row=0;row<rows.size();++row){
            if(row) std::cout<<',';
            std::cout<<'[';
            for(int i=0;i<4;++i){
                if(i) std::cout<<',';
                std::cout<<rows[row].value[i];
            }
            std::cout<<']';
        }
        std::cout << "],\"M4\":[";
        for(int i=0;i<4;++i){
            if(i) std::cout<<',';
            std::cout<<total.value[i];
        }
        std::cout << "]}\n";
        return 0;
    } catch(const std::exception &error) {
        std::cerr << error.what() << '\n'; return 1;
    }
}
