function binarize (I, Flag)

J = imread(I);
h = fspecial('motion', 20, 25);
fI = imfilter(J, h);

hi = 0.5;
lo = 0.4;

if strcmp(Flag, 'high')
    BW = contrast(lo , hi + 0.2, fI);
elseif strcmp(Flag, 'low')
    BW = contrast(lo - 0.2 , hi, fI);
else
    BW = contrast(lo , hi, fI);
end

imwrite(BW,'contrast.png','png')