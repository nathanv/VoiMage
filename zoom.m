% IJ : Input Image. mag: magnification factor. xpos: origin x coordinate
% ypos : origin y coordinate
% Z : out image of section of interest. 

function[Z] = zoom(IJ,mag, xpos, ypos)

hFig = figure('Toolbar','none','Menubar','none');
hIm = imshow(IJ);

hSP = imscrollpanel(hFig,hIm);

hMagBox = immagbox(hFig,hIm);
pos = get(hMagBox,'Position');
set(hMagBox,'Position',[0 0 pos(3) pos(4)])

api = iptgetapi(hSP);

api.setVisibleLocation(xpos, ypos)
api.setMagnification(mag)

r = api.getVisibleImageRect();
rr = round(r); 

Z = IJ(rr(2):rr(2)+rr(4),rr(1):rr(1) + rr(3));

saveas(gca,'zoom.png')
csvwrite('zoom.txt',Z)
%imshow(Z)
