--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

DROP DATABASE shorten;
--
-- Name: shorten; Type: DATABASE; Schema: -; Owner: sysadmin
--

CREATE DATABASE shorten WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


ALTER DATABASE shorten OWNER TO sysadmin;

\connect shorten

SET statement_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: add_history(); Type: FUNCTION; Schema: public; Owner: sysadmin
--

CREATE FUNCTION add_history() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
	BEGIN
	    INSERT INTO link_history (id_link, old_real, date_edit) VALUES (NEW.id_link, OLD.real, now());    
	    RETURN new;
	END;
	$$;


ALTER FUNCTION public.add_history() OWNER TO sysadmin;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: link; Type: TABLE; Schema: public; Owner: sysadmin; Tablespace: 
--

CREATE TABLE link (
    id_link integer NOT NULL,
    shortener integer NOT NULL,
    var_part character varying NOT NULL,
    "real" character varying NOT NULL,
    dateadd timestamp with time zone NOT NULL,
    last_edit timestamp with time zone
);


ALTER TABLE public.link OWNER TO sysadmin;

--
-- Name: link_history; Type: TABLE; Schema: public; Owner: sysadmin; Tablespace: 
--

CREATE TABLE link_history (
    id_link_history integer NOT NULL,
    id_link integer NOT NULL,
    old_real character varying NOT NULL,
    date_edit timestamp with time zone NOT NULL
);


ALTER TABLE public.link_history OWNER TO sysadmin;

--
-- Name: link_history_id_link_history_seq; Type: SEQUENCE; Schema: public; Owner: sysadmin
--

CREATE SEQUENCE link_history_id_link_history_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.link_history_id_link_history_seq OWNER TO sysadmin;

--
-- Name: link_history_id_link_history_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sysadmin
--

ALTER SEQUENCE link_history_id_link_history_seq OWNED BY link_history.id_link_history;


--
-- Name: link_id_link_seq; Type: SEQUENCE; Schema: public; Owner: sysadmin
--

CREATE SEQUENCE link_id_link_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.link_id_link_seq OWNER TO sysadmin;

--
-- Name: link_id_link_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sysadmin
--

ALTER SEQUENCE link_id_link_seq OWNED BY link.id_link;


--
-- Name: shortener; Type: TABLE; Schema: public; Owner: sysadmin; Tablespace: 
--

CREATE TABLE shortener (
    id_shortener integer NOT NULL,
    name character varying NOT NULL,
    domain character varying NOT NULL,
    subdir character varying NOT NULL,
    varalpha boolean DEFAULT true,
    varcase boolean DEFAULT true,
    varnum boolean DEFAULT true
);


ALTER TABLE public.shortener OWNER TO sysadmin;

--
-- Name: shortener_id_shortener_seq; Type: SEQUENCE; Schema: public; Owner: sysadmin
--

CREATE SEQUENCE shortener_id_shortener_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.shortener_id_shortener_seq OWNER TO sysadmin;

--
-- Name: shortener_id_shortener_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sysadmin
--

ALTER SEQUENCE shortener_id_shortener_seq OWNED BY shortener.id_shortener;


--
-- Name: id_link; Type: DEFAULT; Schema: public; Owner: sysadmin
--

ALTER TABLE ONLY link ALTER COLUMN id_link SET DEFAULT nextval('link_id_link_seq'::regclass);


--
-- Name: id_link_history; Type: DEFAULT; Schema: public; Owner: sysadmin
--

ALTER TABLE ONLY link_history ALTER COLUMN id_link_history SET DEFAULT nextval('link_history_id_link_history_seq'::regclass);


--
-- Name: id_shortener; Type: DEFAULT; Schema: public; Owner: sysadmin
--

ALTER TABLE ONLY shortener ALTER COLUMN id_shortener SET DEFAULT nextval('shortener_id_shortener_seq'::regclass);


--
-- Name: PK_link; Type: CONSTRAINT; Schema: public; Owner: sysadmin; Tablespace: 
--

ALTER TABLE ONLY link
    ADD CONSTRAINT "PK_link" PRIMARY KEY (id_link);


--
-- Name: PK_link_history; Type: CONSTRAINT; Schema: public; Owner: sysadmin; Tablespace: 
--

ALTER TABLE ONLY link_history
    ADD CONSTRAINT "PK_link_history" PRIMARY KEY (id_link_history);


--
-- Name: PK_shortener; Type: CONSTRAINT; Schema: public; Owner: sysadmin; Tablespace: 
--

ALTER TABLE ONLY shortener
    ADD CONSTRAINT "PK_shortener" PRIMARY KEY (id_shortener);


--
-- Name: UNIQ_name; Type: CONSTRAINT; Schema: public; Owner: sysadmin; Tablespace: 
--

ALTER TABLE ONLY shortener
    ADD CONSTRAINT "UNIQ_name" UNIQUE (name);


--
-- Name: UNIQ_var_part; Type: CONSTRAINT; Schema: public; Owner: sysadmin; Tablespace: 
--

ALTER TABLE ONLY link
    ADD CONSTRAINT "UNIQ_var_part" UNIQUE (var_part);


--
-- Name: FKI_history_link; Type: INDEX; Schema: public; Owner: sysadmin; Tablespace: 
--

CREATE INDEX "FKI_history_link" ON link_history USING btree (id_link);


--
-- Name: FKI_link_shortener; Type: INDEX; Schema: public; Owner: sysadmin; Tablespace: 
--

CREATE INDEX "FKI_link_shortener" ON link USING btree (shortener);


--
-- Name: update_link; Type: TRIGGER; Schema: public; Owner: sysadmin
--

CREATE TRIGGER update_link AFTER UPDATE ON link FOR EACH ROW EXECUTE PROCEDURE add_history();


--
-- Name: FK_history_link; Type: FK CONSTRAINT; Schema: public; Owner: sysadmin
--

ALTER TABLE ONLY link_history
    ADD CONSTRAINT "FK_history_link" FOREIGN KEY (id_link) REFERENCES link(id_link);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

