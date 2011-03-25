function outline(I)

I = imread(I);
h = fspecial('motion', 20, 25);
fI = imfilter(I, h);

BW = contrast(0.4, 0.5, fI);

J = edge(BW,'sobel',...,
        'nothinning'); 

%XFUS = wfusimg(BW,J,'sym4',5,'max','max');

imwrite(J,'edge.png','png');

%[[B,L] = bwboundaries(BW,'noholes');

%imshow(I);
%hold on

%for k = 1:length(B)
%    boundary = B{k};
%    plot(boundary(:,2), boundary(:,1), 'r', 'LineWidth', 2)
%end

%saveas(gca,'edge.png','png')



