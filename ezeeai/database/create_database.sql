
CREATE DATABASE ezeeai;
USE ezeeai;

CREATE TABLE public.users
			(
			id serial PRIMARY KEY NOT NULL,
			username varchar(16),
			email varchar(50),
			password varchar(80)
			)

CREATE UNIQUE INDEX users_id_uindex ON public.users (id)
CREATE UNIQUE INDEX users_username_uindex ON public.users (username)

CREATE TABLE public.usersession
			(
			id serial PRIMARY KEY NOT NULL,
			username varchar(16),
			token varchar(32),
			timestamp timestamp
			)

CREATE UNIQUE INDEX usersession_id_uindex ON public.usersession (id)
CREATE UNIQUE INDEX usersession_username_uindex ON public.usersession (username)
