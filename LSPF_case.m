
function [x_prediction,X1part,Error]=LSPF_case(N,wear,Time,m_setting)

Pp1=[0.01 -10 -10 -1 0.03];
Pp2=[1 10 10 1 0.03];
f=m_setting(1);
d=m_setting(2);

y=wear;
n_data=length(y);
for i=1:n_data
    if i==1
        train_time(i)=Time(i);
    else
        train_time(i)=Time(i)-Time(i-1);
    end
end
time=train_time(1:n_data);
%% initialization of PF particles
for i = 1 : length(Pp1)
    x1part(i,:) = unifrnd(Pp1(i),Pp2(i),1,N);
end

for k = 1 : n_data
%% 1st PF prdiction 
    if k==1
        x1(k,:)= (0.^(1-x1part(4,:))+(f.^x1part(2,:)).*(d.^x1part(3,:)).*time(k).*(1-x1part(4,:))).^(1./(1-x1part(4,:)));
    else
        x1(k,:)=(x1(k-1,:).^(1-x1part(4,:))+(f.^x1part(2,:)).*(d.^x1part(3,:)).*time(k).*(1-x1part(4,:))).^(1./(1-x1part(4,:)));
    end   
    v1hat(k,:)=y(k)-x1(k,:);
    for i=1:N
        w(i)=(1./(sqrt(2.*pi).*x1part(end,i))).*exp(-0.5.*(v1hat(k,i)).^2./x1part(end,i).^2);
    end
    %generalization of weights & resampling
    w = w./sum(w); 
    for i=1:N; CDF(i)=sum(w(1:i));end
    hh=0.1-0.006*k;
    for i=1:N;
        u=rand;
        [~,r]=find(CDF>=u);
        for j=1:length(Pp1)-1
            x1part_(k,j,i)=normrnd(x1part(j,r(1)),hh*abs(x1part(j,r(1))-mean(x1part(j,:))));
            x1part_(k,length(Pp1),i)=x1part(end,r(1));
        end
        %x1part_(k,:,i)=x1part(:,r(1));
        X1(k,i)=x1(k,r(1));
    end
    x1part(:,:)=x1part_(k,:,:);
    x1(k,:)=X1(k,:);
%   x1_estimate(k)=mean(X1(k,:));
    
end   

% X1part(:,:)=x1part_(end,:,:);

% [~,r]=find(index==2)
% for k=1:80
%     XP(k,:)=x1_estimate(k)+normrnd(0,X1part(end,:));
% end
for k=1:n_data
    X1part(:,:)=x1part_(end,:,:);
    if k==1
        XX1(k,:)= (0.^(1-X1part(4,:))+(f.^X1part(2,:)).*(d.^X1part(3,:)).*time(k).*(1-X1part(4,:))).^(1./(1-X1part(4,:)));
    else
        XX1(k,:)=(XX1(k-1,:).^(1-X1part(4,:))+(f.^X1part(2,:)).*(d.^X1part(3,:)).*time(k).*(1-X1part(4,:))).^(1./(1-X1part(4,:)));
    end   
end

% for i=1:N
%     k=n_data+1;
%     while (((k.*X1part(2,i)).*(1-X1part(1,i))+0.35.^(1-X1part(1,i))).^(1./(1-X1part(1,i))))<1;
%         k=k+1;
%     end
 % end

 x_prediction=prctile(XX1',50);
% plot(1:k,x_prediction,'r',1:k,y,'b');
h1=plot(1:7,wear(1:7),'k*');hold on;pause(2)
for i=1:100
    plot(7:n_data,XX1(7:n_data,i),'color',[210 210 210]/255);hold on;
end
pause(2)

%plot(8:n_data,wear_1(8:n_data),'b-','LineWidth',3);hold on;
h5=plot(8:n_data,XX1(8:n_data,1),'color',[210 210 210]/255);hold on;
h3=plot(8:n_data,x_prediction(8:n_data),'r--','LineWidth',3);hold on;
h4=plot(8:n_data,prctile(XX1(8:n_data,:)',5),'r--','LineWidth',2);hold on;
plot(8:n_data,prctile(XX1(8:n_data,:)',95),'r--','LineWidth',2);hold on;
% h6=plot(201:294,U1_LSPF(:,81:200),'r--','LineWidth',2);hold on;
pause(2)
h2=plot(8:n_data,wear(8:n_data),'b-','LineWidth',3);hold on;
legend([h1,h2,h3,h4,h5],'Measurement','True wear','Median of prediction','90% confidence limits','Prediction paths');

% A=mean(X1part(1,:))
% B=mean(X1part(2,:));
% C=mean(X1part(3,:));
% D=mean(X1part(4,:));
% err=sqrt(sum((x_prediction'-y).^2/(y.^2))/n_data);
% Error=err(end);