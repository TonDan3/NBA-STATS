CREATE TABLE dbo.fact_player_stats_snapshot (
    snapshot_id INT IDENTITY(1,1) NOT NULL,
    player_id INT NOT NULL,
    season VARCHAR(10) NOT NULL,
    snapshot_date DATE NOT NULL,
    games_played INT,
    minutes_avg DECIMAL(10,2),
    points_avg DECIMAL(10,2),
    assists_avg DECIMAL(10,2),
    rebounds_avg DECIMAL(10,2),
    fg_pct DECIMAL(5,2),
    three_pt_made_avg DECIMAL(10,2),
    three_pt_attempt_avg DECIMAL(10,2),
    three_pt_pct DECIMAL(5,2),
    ft_made_avg DECIMAL(10,2),
    ft_attempt_avg DECIMAL(10,2),
    ft_pct DECIMAL(5,2),
    steals_avg DECIMAL(10,2),
    blocks_avg DECIMAL(10,2),
    CONSTRAINT pk_fact_player_snapshot PRIMARY KEY (snapshot_id),
    CONSTRAINT fk_fact_player FOREIGN KEY (player_id)
        REFERENCES dbo.dim_player(player_id),
    CONSTRAINT uq_player_snapshot UNIQUE (player_id, snapshot_date)
);
