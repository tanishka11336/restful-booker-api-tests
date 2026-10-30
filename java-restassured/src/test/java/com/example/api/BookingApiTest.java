package com.example.api;

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import io.restassured.response.Response;
import org.testng.annotations.AfterClass;
import org.testng.annotations.BeforeClass;
import org.testng.annotations.DataProvider;
import org.testng.annotations.Test;

import java.util.HashMap;
import java.util.Map;

import static io.restassured.RestAssured.given;
import static org.hamcrest.Matchers.*;

public class BookingApiTest {

    private String token;
    private int bookingId;

    @BeforeClass
    public void setUp() {
        RestAssured.baseURI = "https://restful-booker.herokuapp.com";

        Map<String, String> credentials = new HashMap<>();
        credentials.put("username", "admin");
        credentials.put("password", "password123");

        token = given()
                .contentType(ContentType.JSON)
                .body(credentials)
                .when().post("/auth")
                .then().statusCode(200)
                .body("token", notNullValue())
                .extract().path("token");
    }

    private Map<String, Object> bookingBody(String first, String last, int price) {
        Map<String, String> dates = new HashMap<>();
        dates.put("checkin", "2026-12-01");
        dates.put("checkout", "2026-12-05");

        Map<String, Object> body = new HashMap<>();
        body.put("firstname", first);
        body.put("lastname", last);
        body.put("totalprice", price);
        body.put("depositpaid", true);
        body.put("bookingdates", dates);
        body.put("additionalneeds", "Breakfast");
        return body;
    }

    @DataProvider(name = "guests")
    public Object[][] guests() {
        return new Object[][]{
                {"Asha", "Patil", 450},
                {"Rohan", "Deshmukh", 1200},
                {"Meera", "Kulkarni", 99}
        };
    }

    @Test(dataProvider = "guests")
    public void createBookingShouldReturnSavedData(String first, String last, int price) {
        int id = given()
                .contentType(ContentType.JSON)
                .accept(ContentType.JSON)
                .body(bookingBody(first, last, price))
                .when().post("/booking")
                .then().statusCode(200)
                .body("booking.firstname", equalTo(first))
                .body("booking.lastname", equalTo(last))
                .body("booking.totalprice", equalTo(price))
                .body("booking.bookingdates.checkin", equalTo("2026-12-01"))
                .extract().path("bookingid");

        // clean up
        given().cookie("token", token).when().delete("/booking/" + id).then().statusCode(201);
    }

    @Test
    public void getBookingByIdShouldReturnBooking() {
        bookingId = given()
                .contentType(ContentType.JSON)
                .accept(ContentType.JSON)
                .body(bookingBody("Lookup", "Test", 300))
                .when().post("/booking")
                .then().statusCode(200)
                .extract().path("bookingid");

        given().accept(ContentType.JSON)
                .when().get("/booking/" + bookingId)
                .then().statusCode(200)
                .body("firstname", equalTo("Lookup"))
                .body("lastname", equalTo("Test"))
                .body("depositpaid", equalTo(true));
    }

    @Test(dependsOnMethods = "getBookingByIdShouldReturnBooking")
    public void updateWithoutTokenShouldBeForbidden() {
        given().contentType(ContentType.JSON)
                .accept(ContentType.JSON)
                .body(bookingBody("No", "Token", 1))
                .when().put("/booking/" + bookingId)
                .then().statusCode(403);
    }

    @Test(dependsOnMethods = "updateWithoutTokenShouldBeForbidden")
    public void deleteBookingShouldReturn201ThenNotFound() {
        given().cookie("token", token)
                .when().delete("/booking/" + bookingId)
                .then().statusCode(201);

        Response response = given().when().get("/booking/" + bookingId);
        response.then().statusCode(404);
    }

    @AfterClass
    public void tearDown() {
        // nothing to release; kept for framework symmetry
    }
}
