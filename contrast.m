% FI : input image. hi: upper contrast threshold. lo: lower contast
% threshold.
% BW1 : output binary image 

function BW1 = contrast(lo, hi, fI)
image = imread(fI);
J = rgb2gray(image);

H = histeq(J);

G = imfill(H,'holes');

S1 = imadjust(G,[lo hi],[]);

F1 = ordfilt2(S1,25,true(5));

new_image = imextendedmax(F1,8);

imwrite(new_image, 'tmp.jpg', 'jpeg');
BW1 = 'tmp.jpg';



