function outlineBox (I,xmin, ymin, width,height)
I = imread(I);

J = I(ymin:ymin+height,xmin:xmin+width,:);

h = fspecial('motion', 20, 25);
fI = imfilter(J, h);

BW = contrast(0.4, 0.5, fI);

Y = edge(BW,'sobel',...,
        'nothinning'); 

imwrite(Y,'edgebox.png','png');