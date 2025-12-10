-- Base y configuración
CREATE DATABASE IF NOT EXISTS dned CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE dned;

-- Tabla: period
CREATE TABLE IF NOT EXISTS period (
    cod_period        VARCHAR(50)  PRIMARY KEY,
    initial_date      DATE         NOT NULL,
    final_date        DATE         NOT NULL,
    description       VARCHAR(255) NULL,
    CHECK (final_date >= initial_date)
) ENGINE=InnoDB;

-- Tabla: user_workspace
CREATE TABLE IF NOT EXISTS user_workspace (
    user_workspace_id VARCHAR(50) PRIMARY KEY,
    space             VARCHAR(100) NOT NULL,
    last_connection   DATETIME     NULL,
    active            BOOLEAN      NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

-- Tabla: user_unal
CREATE TABLE IF NOT EXISTS user_unal (
    email_unal  VARCHAR(100) PRIMARY KEY,
    document    VARCHAR(50)  NOT NULL,
    name        VARCHAR(100) NOT NULL,
    lastname    VARCHAR(100) NOT NULL,
    full_name   VARCHAR(200) NULL,
    gender      VARCHAR(10)  NULL,
    birth_date  DATE         NULL,
    headquarters VARCHAR(100) NULL
) ENGINE=InnoDB;

-- Tabla: user_workspace_associate  (PK compuesta y FK a user_workspace)
CREATE TABLE IF NOT EXISTS user_workspace_associate (
    email_unal        VARCHAR(100) NOT NULL,
    user_workspace_id VARCHAR(50)  NOT NULL,
    cod_period        VARCHAR(50)  NOT NULL,
    PRIMARY KEY (email_unal, user_workspace_id, cod_period),
    CONSTRAINT fk_uws_user   FOREIGN KEY (email_unal)        REFERENCES user_unal(email_unal)             ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_uws_space  FOREIGN KEY (user_workspace_id) REFERENCES user_workspace(user_workspace_id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_uws_period FOREIGN KEY (cod_period)        REFERENCES period(cod_period)                ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_uws_period (cod_period),
    INDEX idx_uws_space (user_workspace_id)
) ENGINE=InnoDB;

-- Tabla: unit_unal
CREATE TABLE IF NOT EXISTS unit_unal (
    cod_unit    VARCHAR(50)  PRIMARY KEY,
    email       VARCHAR(100) NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT         NULL,
    type_unit   VARCHAR(50)  NULL
) ENGINE=InnoDB;

-- Tabla: user_unit_associate  (PK compuesta)
CREATE TABLE IF NOT EXISTS user_unit_associate (
    email_unal VARCHAR(100) NOT NULL,
    cod_unit   VARCHAR(50)  NOT NULL,
    cod_period VARCHAR(50)  NOT NULL,
    PRIMARY KEY (email_unal, cod_unit, cod_period),
    CONSTRAINT fk_uua_user   FOREIGN KEY (email_unal) REFERENCES user_unal(email_unal)   ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_uua_unit   FOREIGN KEY (cod_unit)   REFERENCES unit_unal(cod_unit)     ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_uua_period FOREIGN KEY (cod_period) REFERENCES period(cod_period)      ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_uua_unit (cod_unit),
    INDEX idx_uua_period (cod_period)
) ENGINE=InnoDB;

-- Tabla: school
CREATE TABLE IF NOT EXISTS school (
    cod_school   VARCHAR(50)  PRIMARY KEY,
    email        VARCHAR(100) NULL,
    name         VARCHAR(100) NOT NULL,
    description  TEXT         NULL,
    type_facultad VARCHAR(50) NULL
) ENGINE=InnoDB;

-- Tabla: unit_school_associate  (PK compuesta)
CREATE TABLE IF NOT EXISTS unit_school_associate (
    cod_unit   VARCHAR(50) NOT NULL,
    cod_school VARCHAR(50) NOT NULL,
    cod_period VARCHAR(50) NOT NULL,
    PRIMARY KEY (cod_unit, cod_school, cod_period),
    CONSTRAINT fk_usa_unit   FOREIGN KEY (cod_unit)   REFERENCES unit_unal(cod_unit)   ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_usa_school FOREIGN KEY (cod_school) REFERENCES school(cod_school)    ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_usa_period FOREIGN KEY (cod_period) REFERENCES period(cod_period)    ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_usa_school (cod_school),
    INDEX idx_usa_period (cod_period)
) ENGINE=InnoDB;

-- Tabla: headquarters
CREATE TABLE IF NOT EXISTS headquarters (
    cod_headquarters VARCHAR(50)  PRIMARY KEY,
    email            VARCHAR(100) NULL,
    name             VARCHAR(100) NOT NULL,
    description      TEXT         NULL,
    type_facultad    VARCHAR(50)  NULL
) ENGINE=InnoDB;

-- Tabla: school_headquarters_associate  (PK compuesta)
CREATE TABLE IF NOT EXISTS school_headquarters_associate (
    cod_school       VARCHAR(50) NOT NULL,
    cod_headquarters VARCHAR(50) NOT NULL,
    cod_period       VARCHAR(50) NOT NULL,
    PRIMARY KEY (cod_school, cod_headquarters, cod_period),
    CONSTRAINT fk_sha_school       FOREIGN KEY (cod_school)       REFERENCES school(cod_school)             ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sha_headquarters FOREIGN KEY (cod_headquarters) REFERENCES headquarters(cod_headquarters) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_sha_period       FOREIGN KEY (cod_period)       REFERENCES period(cod_period)             ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_sha_headquarters (cod_headquarters),
    INDEX idx_sha_period (cod_period)
) ENGINE=InnoDB;

-- Tabla: type_user
CREATE TABLE IF NOT EXISTS type_user (
    type_user_id VARCHAR(50) PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    description  TEXT         NULL
) ENGINE=InnoDB;

-- Tabla: type_user_association  (ya tenías PK compuesta; agrego NOT NULL/índices)
CREATE TABLE IF NOT EXISTS type_user_association (
    email_unal   VARCHAR(100) NOT NULL,
    type_user_id VARCHAR(50)  NOT NULL,
    cod_period   VARCHAR(50)  NOT NULL,
    PRIMARY KEY (email_unal, type_user_id, cod_period),
    CONSTRAINT fk_tua_user   FOREIGN KEY (email_unal)   REFERENCES user_unal(email_unal)     ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_tua_type   FOREIGN KEY (type_user_id) REFERENCES type_user(type_user_id)   ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_tua_period FOREIGN KEY (cod_period)   REFERENCES period(cod_period)        ON DELETE RESTRICT ON UPDATE CASCADE,
    INDEX idx_tua_type (type_user_id),
    INDEX idx_tua_period (cod_period)
) ENGINE=InnoDB;

-- Tabla central de correos emisores
CREATE TABLE IF NOT EXISTS email_sender (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(254) NOT NULL,
  name  VARCHAR(150) NULL,
  org_type ENUM('GLOBAL','HEADQUARTERS','SCHOOL','UNIT') NOT NULL DEFAULT 'GLOBAL',
  org_code VARCHAR(100) NULL,
  sede_code VARCHAR(100) NULL,
  level ENUM('PRE','POS','ANY') NOT NULL DEFAULT 'ANY',
  role  ENUM('OWNER','MEMBER') NOT NULL DEFAULT 'OWNER',
  priority INT NOT NULL DEFAULT 100,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NULL ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY uq_email (email),
  -- Índices de consulta por ámbito:
  INDEX idx_scope (org_type, org_code, sede_code, level, role, priority)
) ENGINE=InnoDB;

-- Asociación: email_sender con unidad  (PK compuesta)
CREATE TABLE IF NOT EXISTS email_sender_unit (
    sender_id VARCHAR(50) NOT NULL,
    cod_unit  VARCHAR(50) NOT NULL,
    PRIMARY KEY (sender_id, cod_unit),
    CONSTRAINT fk_esu_sender FOREIGN KEY (sender_id) REFERENCES email_sender(email) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_esu_unit   FOREIGN KEY (cod_unit)  REFERENCES unit_unal(cod_unit) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_esu_unit (cod_unit)
) ENGINE=InnoDB;

-- Asociación: email_sender con escuela
CREATE TABLE IF NOT EXISTS email_sender_school (
    sender_id  VARCHAR(50) NOT NULL,
    cod_school VARCHAR(50) NOT NULL,
    PRIMARY KEY (sender_id, cod_school),
    CONSTRAINT fk_ess_sender FOREIGN KEY (sender_id)  REFERENCES email_sender(email) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_ess_school FOREIGN KEY (cod_school) REFERENCES school(cod_school) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_ess_school (cod_school)
) ENGINE=InnoDB;

-- Asociación: email_sender con sede
CREATE TABLE IF NOT EXISTS email_sender_headquarters (
    sender_id        VARCHAR(50) NOT NULL,
    cod_headquarters VARCHAR(50) NOT NULL,
    PRIMARY KEY (sender_id, cod_headquarters),
    CONSTRAINT fk_esh_sender       FOREIGN KEY (sender_id)        REFERENCES email_sender(email) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_esh_headquarters FOREIGN KEY (cod_headquarters) REFERENCES headquarters(cod_headquarters) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_esh_headquarters (cod_headquarters)
) ENGINE=InnoDB;

-- Auth tables
CREATE TABLE IF NOT EXISTS system_user (
    email           VARCHAR(100) PRIMARY KEY,
    created_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    hashed_password VARCHAR(255) NOT NULL,
    state           BOOLEAN      NOT NULL DEFAULT TRUE,
    salt            VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS token (
    jwt_token VARCHAR(512) PRIMARY KEY,
    email     VARCHAR(100) NOT NULL,
    created_at DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_token_user FOREIGN KEY (email) REFERENCES system_user(email) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_token_email (email)
) ENGINE=InnoDB;

-- Tabla: verification_code 
CREATE TABLE IF NOT EXISTS verification_code (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    email       VARCHAR(100) NOT NULL,
    code        VARCHAR(6)   NOT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at  DATETIME     NOT NULL,
    used        BOOLEAN      NOT NULL DEFAULT FALSE,
    CONSTRAINT fk_vc_user FOREIGN KEY (email) REFERENCES system_user(email) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_vc_email (email),
    INDEX idx_vc_code (code),
    INDEX idx_vc_expires (expires_at)
) ENGINE=InnoDB;

