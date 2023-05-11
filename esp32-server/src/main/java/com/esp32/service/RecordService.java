package com.esp32.service;

import com.esp32.domain.Record;

import java.util.List;

public interface RecordService {
    /**
     * 按id查询
     * @param id
     * @return
     */
    public Record getById(Integer id);

    public List<Record> getAll();
}
