function edge(I)

I = imread(I);
h = fspecial('motion', 20, 25);
fI = imfilter(I, h);

BW = contrast(0.4, 0.5, fI);

[B,L] = bwboundaries(BW,'noholes');

imshow(I)
hold on

for k = 1:length(B)
    boundary = B{k};
    plot(boundary(:,2), boundary(:,1), 'w', 'LineWidth', 2)
end

imwrite(BW,'edge.png','png')
