package com.smart.citizen.service;

import com.smart.citizen.dto.feedback.FeedbackRequest;
import com.smart.citizen.dto.feedback.FeedbackResponse;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;

import java.util.List;
import java.util.UUID;

public interface FeedbackService {
    FeedbackResponse submitFeedback(UUID citizenId, FeedbackRequest request);
    FeedbackResponse getFeedbackById(UUID id);
    Page<FeedbackResponse> getFeedbackByCitizenId(UUID citizenId, Pageable pageable);
    List<FeedbackResponse> getFeedbackByApplicationId(UUID applicationId);
    List<FeedbackResponse> getFeedbackByType(String type);
    FeedbackResponse updateFeedbackStatus(UUID id, String status, String resolution);
}

