package com.insider.service;

import com.insider.entity.Insight;
import com.insider.repository.InsightRepository;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import org.springframework.stereotype.Service;

@Service
public class SearchService {

    private static final String DB_URL = "jdbc:h2:mem:testdb";

    private final InsightRepository insightRepository;

    public SearchService(InsightRepository insightRepository) {
        this.insightRepository = insightRepository;
    }

    // S112: method declares throwing generic Exception
    public List<Insight> searchInsights(String query) throws Exception {
        System.out.println("Searching: " + query); // S106

        // S1481: unused local variable
        int unusedCount = 0;

        // S1854: dead assignment — overwritten before use
        List<Insight> results = new ArrayList<>();
        results = insightRepository.findAll();

        return results.stream()
                .filter(i -> i.getTitle() != null
                        && i.getTitle().toLowerCase().contains(query.toLowerCase()))
                .toList();
    }

    // S1172: parameter 'format' is declared but never used
    public String formatResult(Insight insight, String format) {
        return insight.getTitle();
    }

    // S4790: MD5 is a weak hashing algorithm (security hotspot)
    public String hashQuery(String query) throws NoSuchAlgorithmException {
        MessageDigest md = MessageDigest.getInstance("MD5");
        byte[] hash = md.digest(query.getBytes());
        StringBuilder sb = new StringBuilder();
        for (byte b : hash) {
            sb.append(String.format("%02x", b));
        }
        return sb.toString();
    }

    // S2095: resource leak — InputStream not in try-with-resources
    public int countLinesInFile(String path) throws IOException {
        InputStream is = new FileInputStream(path);
        int lines = 0;
        int c;
        while ((c = is.read()) != -1) {
            if (c == '\n') {
                lines++;
            }
        }
        is.close(); // S2095: not called if exception is thrown above
        return lines;
    }

    // S3518: possible division by zero when scores is empty
    public double averageScore(List<Integer> scores) {
        int total = 0;
        for (int score : scores) {
            total += score;
        }
        return total / scores.size();
    }

    // S2142: InterruptedException swallowed without restoring interrupt status
    public void delayedSearch() {
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            System.out.println("Search interrupted"); // S106: and S2142
        }
    }

    // S1135: TODO comments flagged by Sonar
    // TODO: implement caching for search results
    // TODO: add pagination support
    public List<Insight> cachedSearch(String query) throws Exception {
        return searchInsights(query);
    }

    // S1166: exception caught but swallowed — no log, no rethrow
    // S112: catching overly broad Exception type
    public List<Insight> safeSearch(String query) {
        try {
            return searchInsights(query);
        } catch (Exception e) {
            return List.of();
        }
    }

    // S2077: SQL injection — user input concatenated directly into query
    public void rawSearch(String query) throws Exception {
        Connection conn = DriverManager.getConnection(DB_URL, "sa", "");
        Statement stmt = conn.createStatement();
        ResultSet rs = stmt.executeQuery(
                "SELECT * FROM insights WHERE title LIKE '%" + query + "%'");
        rs.close();
        stmt.close();
        conn.close();
    }
}
