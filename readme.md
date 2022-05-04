# Instructions

## INSTALLATION

- First activate the virtual environment using `source/venv/activate`
- Run the package using `python manage.py runserver`
- Run tests using `python manage.py test`

## FEATURES

Following features are available on the project

- User Registration `/api/account/register`
- Login (JWT generation) `/api/account/login`
- See airing movies `/api/shows/all`
- See showtime for a specific movie `/api/shows/<movieID>`
- Book movie tickets (needs to be logged in) `/api/shows/book`
- See all Booking from today `/api/booking/all`
- See all booking from history and today `/api/booking/all?history=True`
- See all booking that are cancelled from today's showtimes `/api/booking/all?cancelled=True`
- See all booking that are cancelled from history and today `/api/booking/all?cancelled=True&history=True`
- Cancel a booking `/api/booking/cancel/<booking_id>`


## TESTING

- Test the project using Unit test cases from commandline
- Use the postman collection `Showtime.postman_collection.json`

### Thanks and regards,
Gourab Saha | gourabsaha@outlook.in