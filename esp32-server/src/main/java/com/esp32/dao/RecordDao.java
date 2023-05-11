package com.esp32.dao;


import com.esp32.domain.Record;
import org.apache.ibatis.annotations.Insert;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Select;

import java.util.List;

// TODO 添加mapper
@Mapper
public interface RecordDao {
    @Select("select * from operation where id = #{id}")
    public Record getById(Integer id);

    @Select("select * from operation ORDER BY id DESC")
    public List<Record> getAll();

    @Insert("INSERT INTO operation (user, operation) VALUES (#{user}, #{operation})")
    public int insertData(Record record);
}
