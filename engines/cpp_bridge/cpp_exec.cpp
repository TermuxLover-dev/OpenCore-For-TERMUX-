#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include "nlohmann/json.hpp"  // header‑only JSON library, can be bundled

using json = nlohmann::json;

int main() {
    std::ios_base::sync_with_stdio(false);
    std::cin.tie(nullptr);

    // Read JSON from stdin
    std::stringstream buffer;
    buffer << std::cin.rdbuf();
    std::string input = buffer.str();

    try {
        json action = json::parse(input);
        std::string type = action["type"];
        json result;

        if (type == "create_file" || type == "modify_file") {
            std::string path = action["_resolved_path"];
            std::string content = action["content"];
            std::ofstream out(path);
            if (!out) {
                result = {{"error", "Cannot open " + path}};
            } else {
                out << content;
                result = {{"status", "ok"}};
            }
        }
        else if (type == "read_file") {
            std::string path = action["_resolved_path"];
            std::ifstream in(path);
            if (!in) {
                result = {{"error", "File not found"}};
            } else {
                std::stringstream ss;
                ss << in.rdbuf();
                result = {{"content", ss.str()}};
            }
        }
        else if (type == "delete_file") {
            std::string path = action["_resolved_path"];
            if (remove(path.c_str()) == 0)
                result = {{"status", "ok"}};
            else
                result = {{"error", "Cannot delete"}};
        }
        else {
            result = {{"error", "Unsupported C++ action type"}};
        }

        std::cout << result.dump() << std::endl;
    } catch (const std::exception& e) {
        json err = {{"error", std::string("C++ parse error: ") + e.what()}};
        std::cout << err.dump() << std::endl;
    }
    return 0;
}
