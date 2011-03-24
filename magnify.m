% IJ : Input Image. mag: magnification factor. xpos: origin x coordinate
% ypos : origin y coordinate
% Z : out image of section of interest. 

function[Z] = magnify(IJ,mag, xpos, ypos)

hIm = imshow(IJ);

hSP = imscrollpanel(1,hIm);

api = iptgetapi(hSP);

loc = api.getVisibleLocation();
xy = [loc(1)+xpos loc(2)+ypos];

api.setMagnification(mag)
api.setVisibleLocation(xy)

r = api.getVisibleImageRect();
rr = round(r); 

Z = IJ(rr(2):rr(2)+rr(4),rr(1):rr(1) + rr(3));

saveas(gca,'zoom.png')
csvwrite('zoom.txt',Z)
%imshow(Z)
