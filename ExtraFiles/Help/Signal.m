T = 3;

fs = 100;
t = 0:1/fs:T-1/fs;

x = sawtooth(2*pi*1*t,1/2);

plot(t,x,LineWidth=6)
xticklabels({'','','','','','',''})
yticks(0)
grid on
% ax = gca
% ax.LineWidth = 3