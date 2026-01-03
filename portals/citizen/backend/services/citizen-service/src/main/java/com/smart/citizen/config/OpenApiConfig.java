package com.smart.citizen.config;

import io.swagger.v3.oas.models.Components;
import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Contact;
import io.swagger.v3.oas.models.info.Info;
import io.swagger.v3.oas.models.info.License;
import io.swagger.v3.oas.models.security.SecurityRequirement;
import io.swagger.v3.oas.models.security.SecurityScheme;
import io.swagger.v3.oas.models.servers.Server;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import java.util.List;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI citizenPortalOpenAPI() {
        Server devServer = new Server();
        devServer.setUrl("http://localhost:8081/citizen/api/v1");
        devServer.setDescription("Development Server");

        Server prodServer = new Server();
        prodServer.setUrl("https://citizen.smart.rajasthan.gov.in");
        prodServer.setDescription("Production Server");

        Contact contact = new Contact();
        contact.setEmail("support@smart.rajasthan.gov.in");
        contact.setName("SMART Platform Support");
        contact.setUrl("https://smart.rajasthan.gov.in");

        License license = new License()
                .name("Government of Rajasthan")
                .url("https://rajasthan.gov.in");

        Info info = new Info()
                .title("SMART Citizen Portal API")
                .version("1.0.0")
                .contact(contact)
                .description("RESTful API documentation for SMART Citizen Portal. " +
                        "This API enables citizens to access government services, apply for schemes, " +
                        "track applications, manage documents, make payments, and provide feedback.")
                .termsOfService("https://rajasthan.gov.in/pages/website-policies")
                .license(license);

        // Define JWT Security Scheme
        SecurityScheme jwtScheme = new SecurityScheme()
                .type(SecurityScheme.Type.HTTP)
                .scheme("bearer")
                .bearerFormat("JWT")
                .description("Enter JWT token obtained from /auth/test-token endpoint");

        Components components = new Components()
                .addSecuritySchemes("bearer-jwt", jwtScheme);

        // Define security requirement (applies to all endpoints by default)
        SecurityRequirement securityRequirement = new SecurityRequirement()
                .addList("bearer-jwt");

        return new OpenAPI()
                .info(info)
                .servers(List.of(devServer, prodServer))
                .components(components)
                .addSecurityItem(securityRequirement);
    }
}

