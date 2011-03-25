function zoomBox(I, xmin, ymin, width,height)

N = ['box' I];
I = imread(I);

J = I(xmin:xmin+width,ymin:ymin+height,:);

magnify(J,N, 2, 0, 0);