__kernel void check_colors(
    __global const uchar *img, 
    int width, 
    int height, 
    int R, 
    int G, 
    int B, 
    int color_tol, 
    int scope_R, 
    int scope_G, 
    int scope_B, 
    int scope_tol, 
    __global uchar *results) 
{
    int x = get_global_id(0);
    int y = get_global_id(1);
    int idx = (y * width + x) * 3;

    if (x < width && y < height) {
        int r = img[idx];
        int g = img[idx + 1];
        int b = img[idx + 2];

        uchar target_detected = (abs(r - R) <= color_tol && abs(g - G) <= color_tol && abs(b - B) <= color_tol);
        uchar scope_detected = (abs(r - scope_R) <= scope_tol && abs(g - scope_G) <= scope_tol && abs(b - scope_B) <= scope_tol);

        results[y * width + x] = (target_detected << 1) | scope_detected;
    }
}
