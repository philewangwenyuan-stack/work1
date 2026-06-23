#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <exception>
#include <limits>
#include <string>
#include <vector>

#include <opencv2/imgcodecs.hpp>
#include <opencv2/imgproc.hpp>

namespace {

constexpr int kOk = 0;
constexpr int kError = 1;

struct BufferResult {
    std::uint8_t* data;
    int size;
    int width;
    int height;
    int channels;
    int status;
    char message[256];
};

struct GridResult {
    std::int16_t* data;
    int width;
    int height;
    double origin_x;
    double origin_y;
    int status;
    char message[256];
};

void set_message(char* dst, const std::string& message) {
    if (dst == nullptr) {
        return;
    }
    std::strncpy(dst, message.c_str(), 255);
    dst[255] = '\0';
}

void clear_buffer(BufferResult* out) {
    if (out == nullptr) {
        return;
    }
    out->data = nullptr;
    out->size = 0;
    out->width = 0;
    out->height = 0;
    out->channels = 0;
    out->status = kError;
    out->message[0] = '\0';
}

void clear_grid(GridResult* out) {
    if (out == nullptr) {
        return;
    }
    out->data = nullptr;
    out->width = 0;
    out->height = 0;
    out->origin_x = 0.0;
    out->origin_y = 0.0;
    out->status = kError;
    out->message[0] = '\0';
}

bool valid_dims(int width, int height) {
    return width > 0 && height > 0 && width <= 100000 && height <= 100000;
}

bool allocate_buffer_from_mat(const cv::Mat& mat, BufferResult* out) {
    if (out == nullptr || mat.empty() || !mat.isContinuous()) {
        return false;
    }
    const std::size_t byte_count = mat.total() * mat.elemSize();
    if (byte_count > static_cast<std::size_t>(std::numeric_limits<int>::max())) {
        set_message(out->message, "image too large");
        return false;
    }
    auto* data = static_cast<std::uint8_t*>(std::malloc(byte_count));
    if (data == nullptr) {
        set_message(out->message, "malloc failed");
        return false;
    }
    std::memcpy(data, mat.data, byte_count);
    out->data = data;
    out->size = static_cast<int>(byte_count);
    out->width = mat.cols;
    out->height = mat.rows;
    out->channels = mat.channels();
    out->status = kOk;
    set_message(out->message, "ok");
    return true;
}

bool allocate_buffer_from_vector(const std::vector<std::uint8_t>& bytes, int width, int height, int channels, BufferResult* out) {
    if (out == nullptr) {
        return false;
    }
    if (bytes.size() > static_cast<std::size_t>(std::numeric_limits<int>::max())) {
        set_message(out->message, "encoded image too large");
        return false;
    }
    auto* data = static_cast<std::uint8_t*>(std::malloc(bytes.size()));
    if (data == nullptr) {
        set_message(out->message, "malloc failed");
        return false;
    }
    if (!bytes.empty()) {
        std::memcpy(data, bytes.data(), bytes.size());
    }
    out->data = data;
    out->size = static_cast<int>(bytes.size());
    out->width = width;
    out->height = height;
    out->channels = channels;
    out->status = kOk;
    set_message(out->message, "ok");
    return true;
}

cv::Mat occupancy_to_bgr_mat(const std::int16_t* grid, int width, int height) {
    cv::Mat image(height, width, CV_8UC3, cv::Scalar(0, 0, 0));
    for (int row = 0; row < height; ++row) {
        const int dst_row = height - 1 - row;
        auto* dst = image.ptr<cv::Vec3b>(dst_row);
        const std::int16_t* src = grid + static_cast<std::size_t>(row) * width;
        for (int col = 0; col < width; ++col) {
            const std::int16_t value = src[col];
            if (value == 0) {
                dst[col] = cv::Vec3b(245, 245, 245);
            } else if (value == 100) {
                dst[col] = cv::Vec3b(45, 45, 45);
            } else if (value < 0) {
                dst[col] = cv::Vec3b(180, 180, 180);
            }
        }
    }
    return image;
}

cv::Mat map_request_bgr_mat(const std::int16_t* grid, int width, int height) {
    cv::Mat image(height, width, CV_8UC3, cv::Scalar(180, 180, 180));
    for (int row = 0; row < height; ++row) {
        const int dst_row = height - 1 - row;
        auto* dst = image.ptr<cv::Vec3b>(dst_row);
        const std::int16_t* src = grid + static_cast<std::size_t>(row) * width;
        for (int col = 0; col < width; ++col) {
            const std::int16_t value = src[col];
            if (value == 0) {
                dst[col] = cv::Vec3b(245, 245, 245);
            } else if (value >= 100) {
                dst[col] = cv::Vec3b(45, 45, 45);
            }
        }
    }
    return image;
}

cv::Mat map_file_gray_mat(const std::int16_t* grid, int width, int height) {
    cv::Mat image(height, width, CV_8UC1, cv::Scalar(205));
    for (int row = 0; row < height; ++row) {
        const int dst_row = height - 1 - row;
        auto* dst = image.ptr<std::uint8_t>(dst_row);
        const std::int16_t* src = grid + static_cast<std::size_t>(row) * width;
        for (int col = 0; col < width; ++col) {
            const std::int16_t value = src[col];
            if (value == 0) {
                dst[col] = 254;
            } else if (value >= 100) {
                dst[col] = 0;
            }
        }
    }
    return image;
}

std::string normalize_ext(const char* ext) {
    std::string out = ext == nullptr ? ".jpg" : std::string(ext);
    if (out.empty()) {
        out = ".jpg";
    }
    if (out[0] != '.') {
        out = "." + out;
    }
    std::transform(out.begin(), out.end(), out.begin(), [](unsigned char ch) {
        return static_cast<char>(std::tolower(ch));
    });
    if (out != ".png" && out != ".jpg" && out != ".jpeg" && out != ".pgm") {
        out = ".jpg";
    }
    return out;
}

cv::Mat resize_with_aspect(const cv::Mat& image, int max_edge) {
    const int bounded_edge = std::max(64, max_edge);
    const int width = image.cols;
    const int height = image.rows;
    const double scale = std::min(static_cast<double>(bounded_edge) / static_cast<double>(std::max(width, height)), 1.0);
    const int new_width = std::max(1, static_cast<int>(std::round(width * scale)));
    const int new_height = std::max(1, static_cast<int>(std::round(height * scale)));
    if (new_width == width && new_height == height) {
        return image.clone();
    }
    cv::Mat resized;
    cv::resize(image, resized, cv::Size(new_width, new_height), 0.0, 0.0, cv::INTER_AREA);
    return resized;
}

bool encode_mat(const cv::Mat& image, const char* ext, int jpeg_quality, BufferResult* out) {
    const std::string encode_ext = normalize_ext(ext);
    std::vector<int> params;
    if (encode_ext == ".jpg" || encode_ext == ".jpeg") {
        params.push_back(cv::IMWRITE_JPEG_QUALITY);
        params.push_back(std::max(1, std::min(100, jpeg_quality)));
    }
    std::vector<std::uint8_t> encoded;
    if (!cv::imencode(encode_ext, image, encoded, params)) {
        set_message(out->message, "cv::imencode failed");
        return false;
    }
    return allocate_buffer_from_vector(encoded, image.cols, image.rows, image.channels(), out);
}

}  // namespace

extern "C" {

void grinder_map_render_free_buffer(std::uint8_t* ptr) {
    std::free(ptr);
}

void grinder_map_render_free_grid(std::int16_t* ptr) {
    std::free(ptr);
}

int grinder_map_render_rotate_grid_i16(
    const std::int16_t* grid,
    int width,
    int height,
    double origin_x,
    double origin_y,
    double resolution,
    double yaw,
    std::int16_t fill_value,
    GridResult* out
) {
    clear_grid(out);
    try {
        if (grid == nullptr || out == nullptr || !valid_dims(width, height)) {
            set_message(out == nullptr ? nullptr : out->message, "invalid input");
            return kError;
        }
        resolution = std::max(std::abs(resolution), 1e-12);
        if (std::abs(yaw) <= 1e-12) {
            const std::size_t count = static_cast<std::size_t>(width) * height;
            auto* data = static_cast<std::int16_t*>(std::malloc(count * sizeof(std::int16_t)));
            if (data == nullptr) {
                set_message(out->message, "malloc failed");
                return kError;
            }
            std::memcpy(data, grid, count * sizeof(std::int16_t));
            out->data = data;
            out->width = width;
            out->height = height;
            out->origin_x = origin_x;
            out->origin_y = origin_y;
            out->status = kOk;
            set_message(out->message, "ok");
            return kOk;
        }

        const double cos_yaw = std::cos(yaw);
        const double sin_yaw = std::sin(yaw);
        const double x0 = origin_x;
        const double y0 = origin_y;
        const double x1 = x0 + static_cast<double>(width) * resolution;
        const double y1 = y0 + static_cast<double>(height) * resolution;
        const double xs[4] = {x0, x1, x0, x1};
        const double ys[4] = {y0, y0, y1, y1};
        double min_x = std::numeric_limits<double>::infinity();
        double max_x = -std::numeric_limits<double>::infinity();
        double min_y = std::numeric_limits<double>::infinity();
        double max_y = -std::numeric_limits<double>::infinity();
        for (int i = 0; i < 4; ++i) {
            const double rx = cos_yaw * xs[i] - sin_yaw * ys[i];
            const double ry = sin_yaw * xs[i] + cos_yaw * ys[i];
            min_x = std::min(min_x, rx);
            max_x = std::max(max_x, rx);
            min_y = std::min(min_y, ry);
            max_y = std::max(max_y, ry);
        }
        const int out_width = std::max(1, static_cast<int>(std::ceil((max_x - min_x) / resolution)));
        const int out_height = std::max(1, static_cast<int>(std::ceil((max_y - min_y) / resolution)));
        if (!valid_dims(out_width, out_height)) {
            set_message(out->message, "rotated grid too large");
            return kError;
        }
        const std::size_t out_count = static_cast<std::size_t>(out_width) * out_height;
        auto* rotated = static_cast<std::int16_t*>(std::malloc(out_count * sizeof(std::int16_t)));
        if (rotated == nullptr) {
            set_message(out->message, "malloc failed");
            return kError;
        }
        std::fill(rotated, rotated + out_count, fill_value);

        for (int row = 0; row < out_height; ++row) {
            const double y_aligned = min_y + (static_cast<double>(row) + 0.5) * resolution;
            auto* dst = rotated + static_cast<std::size_t>(row) * out_width;
            for (int col = 0; col < out_width; ++col) {
                const double x_aligned = min_x + (static_cast<double>(col) + 0.5) * resolution;
                const double x_map = cos_yaw * x_aligned + sin_yaw * y_aligned;
                const double y_map = -sin_yaw * x_aligned + cos_yaw * y_aligned;
                const int src_col = static_cast<int>(std::floor((x_map - x0) / resolution));
                const int src_row = static_cast<int>(std::floor((y_map - y0) / resolution));
                if (src_col >= 0 && src_col < width && src_row >= 0 && src_row < height) {
                    dst[col] = grid[static_cast<std::size_t>(src_row) * width + src_col];
                }
            }
        }

        out->data = rotated;
        out->width = out_width;
        out->height = out_height;
        out->origin_x = min_x;
        out->origin_y = min_y;
        out->status = kOk;
        set_message(out->message, "ok");
        return kOk;
    } catch (const std::exception& exc) {
        set_message(out == nullptr ? nullptr : out->message, exc.what());
        return kError;
    }
}

int grinder_map_render_occupancy_to_bgr_i16(const std::int16_t* grid, int width, int height, BufferResult* out) {
    clear_buffer(out);
    try {
        if (grid == nullptr || out == nullptr || !valid_dims(width, height)) {
            set_message(out == nullptr ? nullptr : out->message, "invalid input");
            return kError;
        }
        cv::Mat image = occupancy_to_bgr_mat(grid, width, height);
        return allocate_buffer_from_mat(image, out) ? kOk : kError;
    } catch (const std::exception& exc) {
        set_message(out == nullptr ? nullptr : out->message, exc.what());
        return kError;
    }
}

int grinder_map_render_resize_and_encode_u8(
    const std::uint8_t* image,
    int width,
    int height,
    int channels,
    int max_edge,
    const char* ext,
    int jpeg_quality,
    BufferResult* out
) {
    clear_buffer(out);
    try {
        if (image == nullptr || out == nullptr || !valid_dims(width, height) || (channels != 1 && channels != 3)) {
            set_message(out == nullptr ? nullptr : out->message, "invalid input");
            return kError;
        }
        const int cv_type = channels == 1 ? CV_8UC1 : CV_8UC3;
        cv::Mat src(height, width, cv_type, const_cast<std::uint8_t*>(image));
        cv::Mat resized = resize_with_aspect(src, max_edge);
        return encode_mat(resized, ext, jpeg_quality, out) ? kOk : kError;
    } catch (const std::exception& exc) {
        set_message(out == nullptr ? nullptr : out->message, exc.what());
        return kError;
    }
}

int grinder_map_render_encode_map_png_i16(const std::int16_t* grid, int width, int height, BufferResult* out) {
    clear_buffer(out);
    try {
        if (grid == nullptr || out == nullptr || !valid_dims(width, height)) {
            set_message(out == nullptr ? nullptr : out->message, "invalid input");
            return kError;
        }
        cv::Mat image = map_request_bgr_mat(grid, width, height);
        return encode_mat(image, ".png", 90, out) ? kOk : kError;
    } catch (const std::exception& exc) {
        set_message(out == nullptr ? nullptr : out->message, exc.what());
        return kError;
    }
}

int grinder_map_render_write_map_image_i16(const std::int16_t* grid, int width, int height, const char* path) {
    try {
        if (grid == nullptr || path == nullptr || !valid_dims(width, height)) {
            return kError;
        }
        cv::Mat image = map_file_gray_mat(grid, width, height);
        return cv::imwrite(path, image) ? kOk : kError;
    } catch (...) {
        return kError;
    }
}

}  // extern "C"
