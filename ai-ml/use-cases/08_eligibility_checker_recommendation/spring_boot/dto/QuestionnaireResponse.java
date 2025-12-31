package com.smart.platform.eligibility.dto;

import java.util.List;
import java.util.Map;

/**
 * Response DTO for questionnaire template
 */
public class QuestionnaireResponse {
    private Boolean success;
    private String templateName;
    private String templateVersion;
    private List<Question> questions;
    private Map<String, Object> questionFlow;
    private String error;

    // Getters and Setters
    public Boolean getSuccess() {
        return success;
    }

    public void setSuccess(Boolean success) {
        this.success = success;
    }

    public String getTemplateName() {
        return templateName;
    }

    public void setTemplateName(String templateName) {
        this.templateName = templateName;
    }

    public String getTemplateVersion() {
        return templateVersion;
    }

    public void setTemplateVersion(String templateVersion) {
        this.templateVersion = templateVersion;
    }

    public List<Question> getQuestions() {
        return questions;
    }

    public void setQuestions(List<Question> questions) {
        this.questions = questions;
    }

    public Map<String, Object> getQuestionFlow() {
        return questionFlow;
    }

    public void setQuestionFlow(Map<String, Object> questionFlow) {
        this.questionFlow = questionFlow;
    }

    public String getError() {
        return error;
    }

    public void setError(String error) {
        this.error = error;
    }

    // Nested DTO
    public static class Question {
        private String id;
        private String question;
        private String type;  // number, text, select, boolean
        private Boolean required;
        private List<String> options;  // For select type

        // Getters and Setters
        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public String getQuestion() {
            return question;
        }

        public void setQuestion(String question) {
            this.question = question;
        }

        public String getType() {
            return type;
        }

        public void setType(String type) {
            this.type = type;
        }

        public Boolean getRequired() {
            return required;
        }

        public void setRequired(Boolean required) {
            this.required = required;
        }

        public List<String> getOptions() {
            return options;
        }

        public void setOptions(List<String> options) {
            this.options = options;
        }
    }
}

