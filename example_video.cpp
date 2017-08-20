#define _CRT_SECURE_NO_WARNINGS
#include <string>
#include <sstream>
#include <iomanip>
#include <ctime>
#include "opencv2/opencv.hpp"

using namespace cv;
using namespace std;

void putTextInLeftTop(Mat image, String text) {
    const int font = FONT_HERSHEY_SIMPLEX, padding = 5;
    const double fontScale = 0.6;
    Size s = getTextSize(text, font, fontScale, 1, 0);
    putText(image, text, cvPoint(padding, padding + s.height), font, fontScale, cvScalar(255, 255, 255), 1, 8, false);
}

int main(int, char**)
{
    cout << "Begin" << endl;

    const int fps = 24;
    Size size(640, 480);
    VideoWriter out("video.avi", CV_FOURCC('M', 'J', 'P', 'G'), fps, size, true);
    
    int beginAt = time(0), lastSec = 0;

    while (time(0) - beginAt < 5) {
        if (lastSec != time(0)) {
            for (int frameId = 0; frameId < fps; frameId++) {
                Mat frame = Mat(size, CV_8UC3, cvScalar(0, 0, 0));

                stringstream s;
                s << time(0) - beginAt << " sec";
                s << ", " << size.width << ":" << size.height;
                s << ", " << fps << " fps";
                auto t = time(nullptr);
                auto tm = *localtime(&t);
                s << ", " << put_time(&tm, "%H:%M:%S");
                s << ", #" << frameId;
                putTextInLeftTop(frame, s.str());

                out << frame;
                cout << "frame " << frameId << endl;
            }

            lastSec = time(0);
            cout << "time " << time(0) - beginAt << endl;
        }
    }

    cout << "End" << endl;
}
