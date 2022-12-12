/*==============================================================*/
/* Table: account                                               */
/*==============================================================*/
create table account
(
   acc_id               char(16) not null  comment '',
   bra_name             varchar(20) not null  comment '',
   acc_balance          double not null  comment '',
   acc_type             int not null  comment '',
   acc_open_date        date not null  comment '',
   acc_last_activity_date datetime  comment '',
   primary key (acc_id)
);

/*==============================================================*/
/* Table: branch                                                */
/*==============================================================*/
create table branch
(
   bra_name             varchar(20) not null  comment '',
   bra_city             varchar(20) not null  comment '',
   primary key (bra_name)
);

/*==============================================================*/
/* Table: checking_account                                      */
/*==============================================================*/
create table checking_account
(
   acc_id               char(16) not null  comment '',
   che_overdraft        double not null  comment '',
   primary key (acc_id)
);

/*==============================================================*/
/* Table: contact                                               */
/*==============================================================*/
create table contact
(
   cus_id               varchar(18) not null  comment '',
   con_name             varchar(50) not null  comment '',
   con_phone            varchar(16) not null  comment '',
   con_email            varchar(50) not null  comment '',
   con_relation         varchar(50) not null  comment '',
   primary key (cus_id, con_name)
);

/*==============================================================*/
/* Table: customer                                              */
/*==============================================================*/
create table customer
(
   cus_id               varchar(18) not null  comment '',
   cus_name             varchar(50) not null  comment '',
   cus_phone            varchar(16) not null  comment '',
   cus_address          varchar(50) not null  comment '',
   primary key (cus_id)
);

/*==============================================================*/
/* Table: customer_employee_relation                            */
/*==============================================================*/
create table customer_employee_relation
(
   emp_id               varchar(18) not null  comment '',
   cus_id               varchar(18) not null  comment '',
   type                 int not null  comment '',
   primary key (emp_id, cus_id)
);

/*==============================================================*/
/* Table: customer_has_checking_account                         */
/*==============================================================*/
create table customer_has_checking_account
(
   cus_id               varchar(18) not null  comment '',
   acc_id               char(16) not null  comment '',
   primary key (cus_id, acc_id)
);

/*==============================================================*/
/* Table: customer_has_savings_account                          */
/*==============================================================*/
create table customer_has_savings_account
(
   cus_id               varchar(18) not null  comment '',
   acc_id               char(16) not null  comment '',
   primary key (cus_id, acc_id)
);

/*==============================================================*/
/* Table: customer_loan_relation                                */
/*==============================================================*/
create table customer_loan_relation
(
   cus_id               varchar(18) not null  comment '',
   loa_id               bigint not null  comment '',
   primary key (cus_id, loa_id)
);

/*==============================================================*/
/* Table: departement_manager                                   */
/*==============================================================*/
create table departement_manager
(
   bra_name             varchar(20) not null  comment '',
   dep_id               bigint not null  comment '',
   emp_id               varchar(18) not null  comment '',
   primary key (bra_name, dep_id, emp_id)
);

/*==============================================================*/
/* Table: department                                            */
/*==============================================================*/
create table department
(
   bra_name             varchar(20) not null  comment '',
   dep_id               bigint not null  comment '',
   dep_name             varchar(20) not null  comment '',
   dep_type             varchar(20) not null  comment '',
   primary key (bra_name, dep_id)
);

/*==============================================================*/
/* Table: employee                                              */
/*==============================================================*/
create table employee
(
   emp_id               varchar(18) not null  comment '',
   bra_name             varchar(20) not null  comment '',
   dep_id               bigint not null  comment '',
   emp_name             varchar(50) not null  comment '',
   emp_phone            varchar(16) not null  comment '',
   emp_address          varchar(50) not null  comment '',
   start_date           date not null  comment '',
   primary key (emp_id)
);

/*==============================================================*/
/* Table: loan                                                  */
/*==============================================================*/
create table loan
(
   loa_id               bigint not null  comment '',
   bra_name             varchar(20) not null  comment '',
   loa_amount           double not null  comment '',
   loa_date             datetime not null  comment '',
   primary key (loa_id)
);

/*==============================================================*/
/* Table: loan_payment                                          */
/*==============================================================*/
create table loan_payment
(
   loa_id               bigint not null comment '',
   loa_pay_id           bigint not null  comment '',
   loa_pay_amount       double not null  comment '',
   loa_pay_date         datetime not null  comment '',
   primary key (loa_id, loa_pay_id)
);

/*==============================================================*/
/* Table: savings_account                                       */
/*==============================================================*/
create table savings_account
(
   acc_id               char(16) not null  comment '',
   sav_interest_rate    double not null  comment '',
   sav_currency         varchar(16) not null  comment '',
   primary key (acc_id)
);

alter table account add constraint FK_ACCOUNT_OPEN_ACCO_BRANCH foreign key (bra_name)
      references branch (bra_name) on delete restrict on update restrict;

alter table checking_account add constraint FK_CHECKING_CHECKING_ACCOUNT foreign key (acc_id)
      references account (acc_id) on delete restrict on update restrict;

alter table contact add constraint FK_CONTACT_CONTACT_R_CUSTOMER foreign key (cus_id)
      references customer (cus_id) on delete restrict on update restrict;

alter table customer_employee_relation add constraint FK_CUSTOMER_CUSTOMER__EMPLOYEE foreign key (emp_id)
      references employee (emp_id) on delete restrict on update restrict;

alter table customer_employee_relation add constraint FK_CUSTOMER_CUSTOMER__CUSTOMER foreign key (cus_id)
      references customer (cus_id) on delete restrict on update restrict;

alter table customer_has_checking_account add constraint FK_CUSTOMER_CUSTOMER__CUSTOMER2 foreign key (cus_id)
      references customer (cus_id) on delete restrict on update restrict;

alter table customer_has_checking_account add constraint FK_CUSTOMER_CUSTOMER__CHECKING foreign key (acc_id)
      references checking_account (acc_id) on delete restrict on update restrict;

alter table customer_has_savings_account add constraint FK_CUSTOMER_CUSTOMER__CUSTOMER3 foreign key (cus_id)
      references customer (cus_id) on delete restrict on update restrict;

alter table customer_has_savings_account add constraint FK_CUSTOMER_CUSTOMER__SAVINGS_ foreign key (acc_id)
      references savings_account (acc_id) on delete restrict on update restrict;

alter table customer_loan_relation add constraint FK_CUSTOMER_CUSTOMER__CUSTOMER4 foreign key (cus_id)
      references customer (cus_id) on delete restrict on update restrict;

alter table customer_loan_relation add constraint FK_CUSTOMER_CUSTOMER__LOAN foreign key (loa_id)
      references loan (loa_id) on delete restrict on update restrict;

alter table departement_manager add constraint FK_DEPARTEM_DEPARTEME_DEPARTME foreign key (bra_name, dep_id)
      references department (bra_name, dep_id) on delete restrict on update restrict;

alter table departement_manager add constraint FK_DEPARTEM_MANAGER_EMPLOYEE foreign key (emp_id)
      references employee (emp_id) on delete restrict on update restrict;

alter table department add constraint FK_DEPARTME_HAS_BRANCH foreign key (bra_name)
      references branch (bra_name) on delete restrict on update restrict;

alter table employee add constraint FK_EMPLOYEE_WORK_AT_DEPARTME foreign key (bra_name, dep_id)
      references department (bra_name, dep_id) on delete restrict on update restrict;

alter table loan add constraint FK_LOAN_RELEASE_L_BRANCH foreign key (bra_name)
      references branch (bra_name) on delete restrict on update restrict;

alter table loan_payment add constraint FK_LOAN_PAY_PAY_LOAN__LOAN foreign key (loa_id)
      references loan (loa_id) on delete restrict on update restrict;

alter table savings_account add constraint FK_SAVINGS__SAVING_ACCOUNT foreign key (acc_id)
      references account (acc_id) on delete restrict on update restrict;

