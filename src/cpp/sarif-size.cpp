#include <simdjson.h>
#include <iostream>
#include <unordered_map>
#include <vector>
#include <algorithm>
using namespace std;
using namespace simdjson;

size_t size_of_value(ondemand::value v);

// ------------------------------------------------------------------
void walk(ondemand::value v, const string &path,
          unordered_map<string, size_t> &sizes) {
    auto type_res = v.type();
    if (type_res.error()) return;
    ondemand::json_type type = type_res.value();

    sizes[path] += size_of_value(v);

    if (type == ondemand::json_type::object) {
        auto obj = v.get_object();
        if (obj.error()) return;
        for (auto field : obj.value()) {
            auto keyr = field.unescaped_key();
            auto valr = field.value();
            if (keyr.error() || valr.error()) continue;
            walk(valr.value(), path + "." + string(keyr.value()), sizes);
        }
    } else if (type == ondemand::json_type::array) {
        auto arr = v.get_array();
        if (arr.error()) return;
        size_t i = 0;
        for (auto elem : arr.value()) {
            walk(elem.value(), path + "[" + to_string(i++) + "]", sizes);
        }
    }
}

// ------------------------------------------------------------------
size_t size_of_value(ondemand::value v) {
    auto type_res = v.type();
    if (type_res.error()) return 0;
    ondemand::json_type type = type_res.value();

    switch (type) {
    case ondemand::json_type::string:
        return v.get_string().value().size();
    case ondemand::json_type::number:
    case ondemand::json_type::boolean:
    case ondemand::json_type::null:
        return 8;
    case ondemand::json_type::array: {
        size_t s = 0;
        auto arr = v.get_array();
        if (arr.error()) return 0;
        for (auto e : arr.value())
            s += size_of_value(e.value());
        return s;
    }
    case ondemand::json_type::object: {
        size_t s = 0;
        auto obj = v.get_object();
        if (obj.error()) return 0;
        for (auto f : obj.value())
            s += f.unescaped_key().value().size() +
                size_of_value(f.value().value());
        return s;
    }
    default:
        return 0;
    }
}

// ------------------------------------------------------------------
int main(int argc, char **argv) {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <jsonfile>\n";
        return 1;
    }

    ondemand::parser parser;
    padded_string json = padded_string::load(argv[1]);
    ondemand::document doc = parser.iterate(json);

    // Explicitly get the root value once
    ondemand::value root = doc.get_value().value();

    unordered_map<string, size_t> sizes;
    walk(root, "root", sizes);

    vector<pair<string, size_t>> vec(sizes.begin(), sizes.end());
    sort(vec.begin(), vec.end(),
         [](auto &a, auto &b) { return b.second < a.second; });

    for (size_t i = 0; i < min<size_t>(50, vec.size()); ++i)
        cout << vec[i].second << "\t" << vec[i].first << "\n";
}
