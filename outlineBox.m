function outlineBox (I,pos)

I = imread(I);

J = I([pos(1) pos(2) pos(1)+pos(3) pos(2)+pos(4)]);

h = fspecial('motion', 20, 25);
fI = imfilter(J, h);

BW = contrast(0.4, 0.5, fI);

Y = edge(BW,'sobel',...,
        'nothinning'); 

imwrite(Y,'edge.png','png');