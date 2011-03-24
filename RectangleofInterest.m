% x and y are the original x and y coordinate, w is width, h is height,
% in case of more iterations, m is magnification factor, dx and dy are
% offests in the x and y

function RectangleofInterest(pos,m,dx,dy,k)

if (pos(3)*m+dx)/k(2) > 1 
    
    annotation('textarrow',[0.45 0.5],[0.45 0.5],...
                   'String','the x coordinate window is too large.','FontSize',12);
elseif (pos(4)*m+dy)/k(1) > 1 
 
    annotation('textarrow',[0.45 0.5],[0.45 0.5],...
               'String','the x coordinate window is too large.','FontSize',12);
           
else
    h = imrect(gca, [(pos(1)+dx) (pos(2)+dy) (pos(3)*m+dx) (pos(4)*m+dy)]);
    
    setResizable(h,1)
    %annotation('rectangle',[(pos(1)+dx)/k(1) (pos(2)+dy)/k(2) (pos(3)*m+dx)/k(1) (pos(4)*m+dy)/k(2)]) 
    addNewPositionCallback(h,@(p) title(mat2str(p,3)));

    fcn = makeConstrainToRectFcn('imrect',get(gca,'XLim'),get(gca,'YLim'));
    setPositionConstraintFcn(h,fcn);
    
    % annotation('textarrow',[(pos(1)+(pos(3)/2))/k(2) (pos(3)+dx)*0.5/k(2)],[(pos(2)+(pos(4)/2))/k(1) (pos(4)+pos(2))/k(1)],...
    %              'String','We are here.','FontSize',14);
    %saveas(gca,[N '_cluster.bmp']);
end
 
saveas(gca,'box.png')
csvwrite('box.txt',[(pos(1)+dx) (pos(2)+dy) (pos(3)*m+dx) (pos(4)*m+dy)])
