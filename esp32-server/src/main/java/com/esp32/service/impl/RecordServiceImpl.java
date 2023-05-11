package com.esp32.service.impl;

import com.esp32.controller.RecordController;
import com.esp32.domain.Record;
import com.esp32.service.RecordService;
import org.springframework.beans.factory.annotation.Autowired;

import java.util.List;

public class RecordServiceImpl implements RecordService {
    @Autowired
    RecordController recordController;


    @Override
    public Record getById(Integer id) {
        return recordController.getByid(id);
    }

    @Override
    public List<Record> getAll() {
        return null;
    }
}
