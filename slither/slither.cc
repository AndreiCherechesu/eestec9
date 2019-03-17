#include <opencv2/opencv.hpp>
#include <opencv2/highgui.hpp>
#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <unistd.h>
#include <vector>

class Mouse {
 public:
  Mouse() {
    display_ = XOpenDisplay(0);
    int screen = XDefaultScreen(display_);
    root_window_ = XRootWindow(display_, screen);
    w_ = DisplayWidth(display_, screen);
    h_ = DisplayHeight(display_, screen);
    std::cout << "Screen size is " << w_ << "x" << h_ << "." << std::endl;
  }

  ~Mouse() {
    XCloseDisplay(display_);
  }

  void Move(int x, int y) {
    XWarpPointer(display_, None, root_window_, 0, 0, 0, 0, x, y);
    XFlush(display_);
  }

  int max_x() { return w_; }
  int max_y() { return h_; }

 private:
  Display* display_;
  Window root_window_;
  int w_, h_;
};

class Screenshot {
 public:
  Screenshot() {
    display_ = XOpenDisplay(0);
    int screen = XDefaultScreen(display_);
    root_window_ = XRootWindow(display_, screen);
    w_ = DisplayWidth(display_, screen);
    h_ = DisplayHeight(display_, screen);
    img_ = nullptr;
  }

  ~Screenshot() {
    if (img_) {
      XDestroyImage(img_);
      img_ = nullptr;
    }
    XCloseDisplay(display_);
  }

  void Grab(cv::Mat* mat) {
    if (img_) {
      XDestroyImage(img_);
      img_ = nullptr;
    }
    img_ = XGetImage(display_, root_window_, 0, 0, w_ / 2, h_, AllPlanes, ZPixmap);
    *mat = cv::Mat(h_, w_ / 2, CV_8UC4, img_->data);
  }

 private:
  Display* display_;
  Window root_window_;
  int w_, h_;
  XImage* img_;
};

int main() {
  cv::Mat mat;
  Screenshot s;

  int threshold_value = 80;
  int max_target_contour_area = 500;
  int morph_size = 12;

  cv::Point head(480, 565);
  Mouse mouse;

  while (true) {
    s.Grab(&mat);
    cv::Mat pimg, simg, blur;
    mat.copyTo(pimg);
    cv::cvtColor(pimg, pimg, cv::COLOR_RGB2GRAY);

    cv::threshold(pimg, pimg, threshold_value, 255, cv::THRESH_BINARY);
    cv::morphologyEx(pimg, pimg, cv::MORPH_CLOSE,
        cv::getStructuringElement(2,
                              cv::Size(2 * morph_size + 1, 2 * morph_size + 1),
                              cv::Point(morph_size, morph_size)));
    std::vector<std::vector<cv::Point>> contours;
    std::vector<cv::Vec4i> hierarchy;
    cv::findContours(pimg, contours, hierarchy, cv::RETR_LIST, cv::CHAIN_APPROX_SIMPLE, cv::Point(0, 0));
    cv::cvtColor(pimg, simg, cv::COLOR_GRAY2RGB);
    std::vector<cv::Point> targets;
    for (const std::vector<cv::Point>& contour : contours) {
      if (cv::contourArea(contour) > max_target_contour_area) continue;
      int x_sum = 0, y_sum = 0;
      for (const cv::Point& point : contour) {
        x_sum += point.x;
        y_sum += point.y;
      }
      cv::Point target_center(x_sum / contour.size(), y_sum / contour.size());
      cv::circle(simg, target_center, 10, cv::Scalar(0, 0, 255, 0), 2);
      targets.push_back(target_center);
    }
    cv::circle(simg, head, 10, cv::Scalar(0, 255, 0, 0), 2);
    double mind = 10000000.0;
    cv::Point selected_target(0, 0);
    for (const cv::Point& t : targets) {
      double dx = t.x - head.x;
      double dy = t.y - head.y;
      double d = sqrt(dx * dx + dy * dy);
      if (d > 200) continue;
      if (d < mind) {
        mind = d;
        selected_target = t;
      }
    }
    if (selected_target.x == 0 && selected_target.y == 0) {
      std::cout << "No selected target." << std::endl;
    } else {
      mouse.Move(selected_target.x, selected_target.y);
    }
    cv::resize(simg, simg, cv::Size(simg.cols * 0.75, simg.rows * 0.75), 0, 0, CV_INTER_LINEAR);
    cv::imshow("img", simg);
    cv::moveWindow("img", 1000, 100);
    cv::createTrackbar("threshold", "img", &threshold_value, 255);
    cv::createTrackbar("target_area", "img", &max_target_contour_area, 800);
    cv::createTrackbar("morph_size", "img", &morph_size, 20);
    if (cv::waitKey(1) == 27) break;
  }
  return 0;
}
