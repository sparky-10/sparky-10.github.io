close all;
clear variables;
clc;

%%

% File info
folder = 'images';
files = {   'Flat wall', "Absorbing wall", "Concave wall", "Convex wall", ...
            "Schroeder diffuser", "Binary amplitude diffuser", "Helmholtz resonator", ...
            "Box room", "Whispering gallery", "Square object", "Circular object", "Barrier", ...
            "Single slit", "Double slit", "Perforated sheet", "Sonic crystal", ...
            "Squiggle", "Hello world", "Maze"};
ext = 'png';

% List of examples to use and pyconfig file
jsFile = '../exampleList.js';
tomlFile = '../pyConfig.toml';

% Deafult grid size
Nx = 300;
Ny = 200;

%%

% Open files
fid1 = fopen(jsFile,'w+');
fid2 = fopen(tomlFile,'w+');

% Start of js file
fwrite(fid1,'var imList = [');

% Some non image file stuff we need in the toml
fwrite(fid2, ['packages = ["numpy", "matplotlib", "scipy"]', newline, ...
    'plugins = []', newline, ...
    '[[fetch]]', newline, ...
    'files = ["./pyFDTD/pyFDTD.py"']);

% No. of files
NFiles = length(files);

% loop round all
for i = 1:NFiles
    % write new items to file
    if i > 1;   fwrite(fid1,', ');   end
    fwrite(fid1,sprintf('"%s"',files{i}));
    filei = strrep(files{i},' ','_');
    saveFileStr = sprintf('%s.%s',filei,ext);
    fidFileStr = sprintf('./%s/%s',folder,saveFileStr);
    stri = sprintf(', "%s"',fidFileStr);
    fwrite(fid2,stri);
    % Default empty image
    switch files{i}
        case "Whispering gallery"
            Nxi = 250;
            Nyi = 250;
        case "Binary amplitude diffuser"
            NSeqRep = 3;
            Nyi = 7*12*NSeqRep;
            Nxi = Nyi;
        case "Schroeder diffuser"
            NSeqRep = 3;
            Nyi = 7*12*NSeqRep;
            Nxi = Nyi;
        otherwise
            Nxi = Nx;
            Nyi = Ny;
    end
    im = zeros(Nyi,Nxi);
    xx = repmat(1:Nxi,Nyi,1);
    yy = repmat((1:Nyi).',1,Nxi);
    xMid = (Nxi+1)*0.5;
    yMid = (Nyi+1)*0.5;
    xMidInt = ceil(xMid);
    yMidInt = ceil((Nyi+1)*0.5);
    barrierWidth = Nxi*0.02;
    % Process depending on image type
    switch files{i}
        case 'Flat wall'
            depth = ceil(Nxi*0.05);
            xInds = ((1-depth):0)+Nxi;
            im(:,xInds) = 1;
        case "Absorbing wall"
            depth = ceil(Nxi*0.05);
            xInds = ((1-depth):0)+Nxi;
            im(:,xInds) = 1;
        case "Concave wall"
            x0 = Nxi*0.4;
            y0 = yMidInt;
            borderPad = 0.02*Nxi;
            r = sqrt(((xx+borderPad)-x0).^2+(yy-y0).^2);
            im(r>(Nxi-x0)&xx>xMidInt) = 1;
        case "Convex wall"
            x0 = Nxi+xMidInt;
            y0 = yMidInt;
            borderPad = 0.02*Nxi;
            r = sqrt(((xx+borderPad)-x0).^2+(yy-y0).^2);
            im(r<(Nxi*0.65)) = 1;
        case "Schroeder diffuser"
            depth = ceil(Nxi*0.08);
            QSeq = [0,1,4,2,2,4,1];
            NQSeq = length(QSeq);
            wellStepDepth = floor(depth/max(QSeq));
            finWidth = 1;
            patchWidth = round(Nyi/NQSeq/NSeqRep)-finWidth;
            NRep = Nyi/NQSeq/patchWidth;
            xInds = ((1-depth):0)+Nxi;
            im(:,xInds) = 1;
            yInds = (1:patchWidth);
            for j = 1:NRep
                for k = 1:NQSeq
                    xInds = Nxi-depth+(1:QSeq(k)*wellStepDepth);
                    im(yInds,xInds) = 0;
                    yInds = yInds+patchWidth+finWidth;
                end
            end
        case "Binary amplitude diffuser"
            depth = ceil(Nxi*0.08);
            MSeq = [1,1,0,0,1,0,1];
            NMSeq = length(MSeq);
            patchWidth = round(Nyi/NMSeq/NSeqRep);
            NRep = Nyi/NMSeq/patchWidth;
            xInds = ((1-depth):0)+Nxi;
            im(:,xInds) = 1;
            yInds = find(repmat(kron(MSeq(:),ones([patchWidth,1])),[NRep,1]));
            im(yInds,xInds) = 0.05;
        case "Helmholtz resonator"
            x0 = xMidInt;
            neckWidth = Nxi*0.05;
            cavityWidth = Nxi*0.15;
            y1 = ceil(Nyi*0.7);
            y2 = ceil(Nyi*0.75);
            y3 = ceil(Nyi*0.9);
            inds = y1<yy;
            im(inds) = 1;
            xInds = abs(xx-x0)<neckWidth*0.5;
            yInds = y1<=yy&y2>yy;
            im(xInds&yInds) = 0;
            xInds = abs(xx-x0)<cavityWidth*0.5;
            yInds = y2<=yy&y3>yy;
            im(xInds&yInds) = 0;
        case "Box room"
            % Nothing to see here
        case "Whispering gallery"
            x0 = xMid;
            y0 = yMid;
            borderPad = Nxi*0.01;
            r = sqrt((xx-x0).^2+(yy-y0).^2);
            im(r>(Nxi*0.5-borderPad)) = 1;
        case "Square object"
            x0 = Nxi*0.75;
            y0 = yMidInt;
            dx = xx-x0;
            dy = yy-y0;
            im(abs(dx)<Nxi/8&abs(dy)<Nxi/8) = 1;
        case "Circular object"
            x0 = Nxi*0.75;
            y0 = yMidInt;
            r = sqrt((xx-x0).^2+(yy-y0).^2);
            im(r<Nxi/8) = 1;
        case "Barrier"
            x0 = xMidInt;
            y0 = yMidInt;
            dx = xx-x0;
            dy = yy-y0;
            im(abs(dx)<barrierWidth*0.5&dy>0) = 1;
        case "Single slit"
            x0 = xMidInt;
            y0 = yMidInt;
            slitSize = Nyi*1/20;
            dx = xx-x0;
            dy = yy-y0;
            im(abs(dx)<barrierWidth*0.5) = 1;
            im(abs(dy)<slitSize*0.5) = 0;
        case "Double slit"
            x0 = xMidInt;
            y0 = yMidInt;
            slitSize = Nyi*1/20;
            slitSpace = slitSize*4;
            dx = xx-x0;
            dy = yy-y0;
            im(abs(dx)<barrierWidth*0.5) = 1;
            im(abs(dy+slitSpace*0.5)<slitSize*0.5) = 0;
            im(abs(dy-slitSpace*0.5)<slitSize*0.5) = 0;
        case "Perforated sheet"
            x0 = xMidInt;
            y0 = yMidInt;
            slitSize = Nyi*1/20;
            slitSpace = slitSize*4;
            dx = xx-x0;
            dy = yy-y0;
            im(abs(dx)<barrierWidth*0.5) = 1;
            im(mod(dy+slitSize*0.5,slitSpace)<slitSize) = 0;
        case "Sonic crystal"
            xStep = floor(Nyi/8);
            x0 = xMidInt:xStep:Nxi;
            y0 = xStep*0.5:xStep:Nyi;
            Nx0 = length(x0);
            Ny0 = length(y0);
            rLim = floor(Nyi/(4*Ny0));
            for j = 1:Nx0
                for k = 1:Ny0
                    r = sqrt((xx-x0(j)).^2+(yy-y0(k)).^2);
                    im(r<rLim) = 1;
                end
            end
        case "Squiggle"
            fileStrLoad = sprintf('%s_orig.%s',filei,ext);
            im = imread(fileStrLoad);
            im = 1-mean(im,3)/double(max(im(:)));
            im = ceil(im-0.5);
%             imagesc(im)
        case "Hello world"
            fileStrLoad = sprintf('%s_orig.%s',filei,ext);
            [im,map] = imread(fileStrLoad);
            im = 1-mean(im,3)/double(max(im(:)));
            im = ceil(im-0.9);
%             imagesc(im)
        case "Maze"
            fileStrLoad = sprintf('%s_orig.%s',filei,ext);
            im = imread(fileStrLoad);
            im = 1-mean(im,3)/double(max(im(:)));
            im = ceil(im-0.1);
%             imagesc(im)
    end
    % Image is inverse of above
    im = 1-im;
    % Write image to file
    imwrite(im,saveFileStr);
end

% End text
fwrite(fid1,'];');
fwrite(fid1,[newline, 'var imExt = "', ext, '";']);
fwrite(fid2,']');

% Close files
fclose(fid1);
fclose(fid2);

