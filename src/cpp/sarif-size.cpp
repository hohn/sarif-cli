#include <simdjson.h>
#include <iostream>
#include <unordered_map>
#include <vector>
#include <algorithm>
using namespace std;
using namespace simdjson;

size_t sizeof_json(dom::element e) {
    switch (e.type()) {
    case dom::element_type::STRING: return e.get_string().value().size();
    case dom::element_type::INT64:
    case dom::element_type::UINT64:
    case dom::element_type::DOUBLE:
    case dom::element_type::BOOL:
    case dom::element_type::NULL_VALUE: return 8;
    case dom::element_type::ARRAY: {
        size_t s = 0; for (auto v : e.get_array()) s += sizeof_json(v); return s;
    }
    case dom::element_type::OBJECT: {
        size_t s = 0; for (auto [k,v] : e.get_object()) s += k.size() + sizeof_json(v); return s;
    }
    }
    return 0;
}

void walk(dom::element e, string path, unordered_map<string,size_t>& sizes) {
    sizes[path] += sizeof_json(e);
    if (e.is_object()) {
        for (auto [k,v]: e.get_object()) walk(v, path + "." + string(k), sizes);
    } else if (e.is_array()) {
        size_t i=0;
        for (auto v: e.get_array()) walk(v, path + "[" + to_string(i++) + "]", sizes);
    }
}

int main(int argc,char**argv){
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <jsonfile>\n";
        return 1;
    }

    simdjson::dom::parser parser;

    auto doc = parser.load(argv[1]);

    unordered_map<string,size_t> sizes;
    walk(doc.value(), "root", sizes);

    vector<pair<string,size_t>> vec(sizes.begin(), sizes.end());
    sort(vec.begin(), vec.end(), [](auto&a,auto&b){return b.second < a.second;});

    for (size_t i=0; i < min<size_t>(50, vec.size()); ++i)
        cout << vec[i].second << "\t" << vec[i].first << "\n";
}
