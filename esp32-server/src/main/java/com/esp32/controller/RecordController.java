package com.esp32.controller;

import com.esp32.dao.RecordDao;
import com.esp32.domain.Record;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.ui.ModelMap;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.ModelAndView;

import java.io.BufferedInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.List;

@RestController
@RequestMapping("/record")
public class RecordController {
    @Autowired
    private RecordDao recordDao;

    // http://127.0.0.1:8080/record/{id}
    @GetMapping("/{id}")
    public Record getByid(@PathVariable Integer id) {
        Record r = recordDao.getById(id);
        System.out.println(r);
        return recordDao.getById(id);
    }


    @RequestMapping(value = "/all", method = RequestMethod.GET)
    public ModelAndView getAll(ModelMap map){
        List<Record> Records = recordDao.getAll();
        System.out.println(Records);
        map.put("r", Records);
        return new ModelAndView("record");
    }

    @GetMapping("/update/{user}&&{operation}")
    public boolean updateRecord(@PathVariable("user") String user, @PathVariable("operation") String operation){
        System.out.println(user + "=======>" + operation);
        return recordDao.insertData(new Record(user, operation)) > 0;
    }

    @GetMapping("/upload")
    public void uploadVideo() throws IOException {
        // 创建服务端  服务端使用的端口是8888
        ServerSocket ss = new ServerSocket(8888);
        //阻塞，只有收到客户端传数据过来之后才会继续往下执行
        Socket socket = ss.accept();
        // 获得客户端传来的数据，通过输入流输入到服务端
        InputStream ips = socket.getInputStream();
        //同样的用缓冲区来获取数据
        BufferedInputStream stream = new BufferedInputStream(ips);
        // 创建文件输出流  用来将服务端获取的数据 输出到这个文件中
        FileOutputStream file = new FileOutputStream(String.valueOf(System.currentTimeMillis()) + ".avi");

        int line = 0;
        //从服务器中一个一个读取数据
        while ((line = stream.read())!=-1) {
            // 拷贝时间可能很长，用一个简单的字符来观察是否正在传输数据，以及观察是否传输完成。
            System.out.println("----");
            //将读取的数据一个一个写入文件中
            file.write(line);
        }
    }
}
