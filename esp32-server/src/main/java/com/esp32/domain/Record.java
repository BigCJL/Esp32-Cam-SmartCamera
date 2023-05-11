package com.esp32.domain;

import java.sql.Timestamp;


public class Record {
    public Integer id;
    private String user;
    private String operation;
    private Timestamp time;

    public Record(Integer id, String user, String operation, Timestamp time) {
        this.id = id;
        this.user = user;
        this.operation = operation;
        this.time = time;
    }

    public Record() {

    }

    public Record(String user, String operation) {
        this.user = user;
        this.operation = operation;
    }

    @Override
    public String toString() {
        return "Record{" +
                "id=" + id +
                ", user='" + user + '\'' +
                ", operation='" + operation + '\'' +
                ", time=" + time +
                '}';
    }

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getUser() {
        return user;
    }

    public void setUser(String user) {
        this.user = user;
    }

    public String getOperation() {
        return operation;
    }

    public void setOperation(String operation) {
        this.operation = operation;
    }

    public Timestamp getTime() {
        return time;
    }

    public void setTime(Timestamp time) {
        this.time = time;
    }
}
