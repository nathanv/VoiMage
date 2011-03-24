% FI : input image. hi: upper contrast threshold. lo: lower contast
% threshold.
% BW1 : output binary image 

function[BW1] = contrast(lo, hi, fI)

J = rgb2gray(fI);

H = histeq(J);

G = imfill(H,'holes');

S1 = imadjust(G,[lo hi],[]);

F1 = ordfilt2(S1,25,true(5));

BW1 = imextendedmax(F1,8);

saveas(gca, 'contrast.png')
