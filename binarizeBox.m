function binarizeBox(I,Flag, xmin, ymin, width,height)

I = imread(I);

J = I(ymin:ymin+height,xmin:xmin+width,:);

h = fspecial('motion', 20, 25);
fI = imfilter(J, h);

hi = 0.5;
lo = 0.4;

if strcmp(Flag, 'high')
    Y = contrast(lo , hi + 0.2, fI);
elseif strcmp(Flag, 'low')
    Y = contrast(lo - 0.2 , hi, fI);
else
    Y = contrast(lo , hi, fI);
end

imwrite(Y,'binarizebox.png','png');