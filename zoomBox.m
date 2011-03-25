function zoomBox(I,pos)

I = imread(I);

J = I([pos(1) pos(2) pos(1)+pos(3) pos(2)+pos(4)]);

magnify(J,I, 2, 0, 0);