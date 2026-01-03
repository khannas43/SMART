package com.smart.citizen.service.impl;

import com.smart.citizen.dto.feedback.FeedbackRequest;
import com.smart.citizen.dto.feedback.FeedbackResponse;
import com.smart.citizen.entity.Citizen;
import com.smart.citizen.entity.Feedback;
import com.smart.citizen.entity.ServiceApplication;
import com.smart.citizen.exception.ResourceNotFoundException;
import com.smart.citizen.mapper.FeedbackMapper;
import com.smart.citizen.repository.CitizenRepository;
import com.smart.citizen.repository.FeedbackRepository;
import com.smart.citizen.repository.ServiceApplicationRepository;
import com.smart.citizen.service.FeedbackService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Transactional
public class FeedbackServiceImpl implements FeedbackService {

    private final FeedbackRepository feedbackRepository;
    private final CitizenRepository citizenRepository;
    private final ServiceApplicationRepository applicationRepository;
    private final FeedbackMapper feedbackMapper;

    @Override
    public FeedbackResponse submitFeedback(UUID citizenId, FeedbackRequest request) {
        // Validate citizen exists
        Citizen citizen = citizenRepository.findById(citizenId)
                .orElseThrow(() -> new ResourceNotFoundException("Citizen", "id", citizenId));

        Feedback feedback = feedbackMapper.toEntity(request);
        feedback.setCitizen(citizen);
        feedback.setStatus(Feedback.FeedbackStatus.OPEN);

        // Set application if provided
        if (request.getApplicationId() != null) {
            ServiceApplication application = applicationRepository.findById(request.getApplicationId())
                    .orElseThrow(() -> new ResourceNotFoundException("ServiceApplication", "id", request.getApplicationId()));
            feedback.setApplication(application);
        }

        Feedback savedFeedback = feedbackRepository.save(feedback);
        return feedbackMapper.toResponse(savedFeedback);
    }

    @Override
    @Transactional(readOnly = true)
    public FeedbackResponse getFeedbackById(UUID id) {
        Feedback feedback = feedbackRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Feedback", "id", id));
        return feedbackMapper.toResponse(feedback);
    }

    @Override
    @Transactional(readOnly = true)
    public Page<FeedbackResponse> getFeedbackByCitizenId(UUID citizenId, Pageable pageable) {
        return feedbackRepository.findByCitizenId(citizenId, pageable)
                .map(feedbackMapper::toResponse);
    }

    @Override
    @Transactional(readOnly = true)
    public List<FeedbackResponse> getFeedbackByApplicationId(UUID applicationId) {
        return feedbackRepository.findByApplicationId(applicationId).stream()
                .map(feedbackMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    @Transactional(readOnly = true)
    public List<FeedbackResponse> getFeedbackByType(String type) {
        Feedback.FeedbackType feedbackType = Feedback.FeedbackType.valueOf(type.toUpperCase());
        return feedbackRepository.findByType(feedbackType).stream()
                .map(feedbackMapper::toResponse)
                .collect(Collectors.toList());
    }

    @Override
    public FeedbackResponse updateFeedbackStatus(UUID id, String status, String resolution) {
        Feedback feedback = feedbackRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Feedback", "id", id));
        
        feedback.setStatus(Feedback.FeedbackStatus.valueOf(status.toUpperCase()));
        if (resolution != null) {
            feedback.setResolution(resolution);
            feedback.setResolvedAt(LocalDateTime.now());
        }
        
        Feedback updatedFeedback = feedbackRepository.save(feedback);
        return feedbackMapper.toResponse(updatedFeedback);
    }
}

