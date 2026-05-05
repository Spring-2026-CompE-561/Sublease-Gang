# scripts/seed_colleges.py
# Run with: python -m scripts.seed_colleges

from app.db import SessionLocal
from app.models.college import College

COLLEGES = [
    # Alabama
    {"name": "University of Alabama", "city": "Tuscaloosa, AL"},
    {"name": "Auburn University", "city": "Auburn, AL"},
    {"name": "University of Alabama at Birmingham", "city": "Birmingham, AL"},
    {"name": "Alabama A&M University", "city": "Normal, AL"},
    {"name": "Samford University", "city": "Birmingham, AL"},
    # Alaska
    {"name": "University of Alaska Fairbanks", "city": "Fairbanks, AK"},
    {"name": "University of Alaska Anchorage", "city": "Anchorage, AK"},
    # Arizona
    {"name": "Arizona State University", "city": "Tempe, AZ"},
    {"name": "University of Arizona", "city": "Tucson, AZ"},
    {"name": "Northern Arizona University", "city": "Flagstaff, AZ"},
    {"name": "Grand Canyon University", "city": "Phoenix, AZ"},
    # Arkansas
    {"name": "University of Arkansas", "city": "Fayetteville, AR"},
    {"name": "Arkansas State University", "city": "Jonesboro, AR"},
    {"name": "University of Central Arkansas", "city": "Conway, AR"},
    # California
    {"name": "University of California, Los Angeles", "city": "Los Angeles, CA"},
    {"name": "University of California, Berkeley", "city": "Berkeley, CA"},
    {"name": "University of California, San Diego", "city": "La Jolla, CA"},
    {"name": "University of California, Davis", "city": "Davis, CA"},
    {"name": "University of California, Santa Barbara", "city": "Santa Barbara, CA"},
    {"name": "University of California, Irvine", "city": "Irvine, CA"},
    {"name": "University of California, Santa Cruz", "city": "Santa Cruz, CA"},
    {"name": "University of California, Riverside", "city": "Riverside, CA"},
    {"name": "University of Southern California", "city": "Los Angeles, CA"},
    {"name": "Stanford University", "city": "Stanford, CA"},
    {"name": "California Institute of Technology", "city": "Pasadena, CA"},
    {"name": "San Diego State University", "city": "San Diego, CA"},
    {"name": "California State University, Long Beach", "city": "Long Beach, CA"},
    {"name": "California State University, Fullerton", "city": "Fullerton, CA"},
    {"name": "California State University, Northridge", "city": "Northridge, CA"},
    {"name": "San Jose State University", "city": "San Jose, CA"},
    {"name": "California Polytechnic State University", "city": "San Luis Obispo, CA"},
    {"name": "Santa Clara University", "city": "Santa Clara, CA"},
    {"name": "Pepperdine University", "city": "Malibu, CA"},
    {"name": "Loyola Marymount University", "city": "Los Angeles, CA"},
    {"name": "University of San Francisco", "city": "San Francisco, CA"},
    {"name": "University of San Diego", "city": "San Diego, CA"},
    {"name": "Chapman University", "city": "Orange, CA"},
    # Colorado
    {"name": "University of Colorado Boulder", "city": "Boulder, CO"},
    {"name": "Colorado State University", "city": "Fort Collins, CO"},
    {"name": "University of Denver", "city": "Denver, CO"},
    {"name": "Colorado School of Mines", "city": "Golden, CO"},
    {"name": "University of Colorado Denver", "city": "Denver, CO"},
    # Connecticut
    {"name": "Yale University", "city": "New Haven, CT"},
    {"name": "University of Connecticut", "city": "Storrs, CT"},
    {"name": "Fairfield University", "city": "Fairfield, CT"},
    {"name": "Trinity College", "city": "Hartford, CT"},
    {"name": "Wesleyan University", "city": "Middletown, CT"},
    # Delaware
    {"name": "University of Delaware", "city": "Newark, DE"},
    {"name": "Delaware State University", "city": "Dover, DE"},
    # Florida
    {"name": "University of Florida", "city": "Gainesville, FL"},
    {"name": "Florida State University", "city": "Tallahassee, FL"},
    {"name": "University of Miami", "city": "Coral Gables, FL"},
    {"name": "University of Central Florida", "city": "Orlando, FL"},
    {"name": "University of South Florida", "city": "Tampa, FL"},
    {"name": "Florida International University", "city": "Miami, FL"},
    {"name": "Florida Atlantic University", "city": "Boca Raton, FL"},
    {"name": "University of North Florida", "city": "Jacksonville, FL"},
    {"name": "Florida A&M University", "city": "Tallahassee, FL"},
    {"name": "Stetson University", "city": "DeLand, FL"},
    {"name": "Rollins College", "city": "Winter Park, FL"},
    {"name": "Nova Southeastern University", "city": "Fort Lauderdale, FL"},
    # Georgia
    {"name": "Georgia Institute of Technology", "city": "Atlanta, GA"},
    {"name": "University of Georgia", "city": "Athens, GA"},
    {"name": "Emory University", "city": "Atlanta, GA"},
    {"name": "Georgia State University", "city": "Atlanta, GA"},
    {"name": "Mercer University", "city": "Macon, GA"},
    {"name": "Morehouse College", "city": "Atlanta, GA"},
    {"name": "Spelman College", "city": "Atlanta, GA"},
    {"name": "Kennesaw State University", "city": "Kennesaw, GA"},
    # Hawaii
    {"name": "University of Hawaii at Manoa", "city": "Honolulu, HI"},
    # Idaho
    {"name": "University of Idaho", "city": "Moscow, ID"},
    {"name": "Boise State University", "city": "Boise, ID"},
    {"name": "Idaho State University", "city": "Pocatello, ID"},
    # Illinois
    {"name": "University of Chicago", "city": "Chicago, IL"},
    {"name": "Northwestern University", "city": "Evanston, IL"},
    {"name": "University of Illinois Urbana-Champaign", "city": "Champaign, IL"},
    {"name": "University of Illinois Chicago", "city": "Chicago, IL"},
    {"name": "Illinois Institute of Technology", "city": "Chicago, IL"},
    {"name": "Loyola University Chicago", "city": "Chicago, IL"},
    {"name": "DePaul University", "city": "Chicago, IL"},
    {"name": "Southern Illinois University", "city": "Carbondale, IL"},
    {"name": "Northern Illinois University", "city": "DeKalb, IL"},
    {"name": "Illinois State University", "city": "Normal, IL"},
    # Indiana
    {"name": "University of Notre Dame", "city": "Notre Dame, IN"},
    {"name": "Purdue University", "city": "West Lafayette, IN"},
    {"name": "Indiana University Bloomington", "city": "Bloomington, IN"},
    {"name": "Butler University", "city": "Indianapolis, IN"},
    {"name": "Ball State University", "city": "Muncie, IN"},
    {"name": "Valparaiso University", "city": "Valparaiso, IN"},
    # Iowa
    {"name": "University of Iowa", "city": "Iowa City, IA"},
    {"name": "Iowa State University", "city": "Ames, IA"},
    {"name": "Drake University", "city": "Des Moines, IA"},
    {"name": "Grinnell College", "city": "Grinnell, IA"},
    # Kansas
    {"name": "University of Kansas", "city": "Lawrence, KS"},
    {"name": "Kansas State University", "city": "Manhattan, KS"},
    {"name": "Wichita State University", "city": "Wichita, KS"},
    # Kentucky
    {"name": "University of Kentucky", "city": "Lexington, KY"},
    {"name": "University of Louisville", "city": "Louisville, KY"},
    {"name": "Western Kentucky University", "city": "Bowling Green, KY"},
    {"name": "Eastern Kentucky University", "city": "Richmond, KY"},
    # Louisiana
    {"name": "Louisiana State University", "city": "Baton Rouge, LA"},
    {"name": "Tulane University", "city": "New Orleans, LA"},
    {"name": "University of New Orleans", "city": "New Orleans, LA"},
    {"name": "Loyola University New Orleans", "city": "New Orleans, LA"},
    {"name": "Louisiana Tech University", "city": "Ruston, LA"},
    # Maine
    {"name": "University of Maine", "city": "Orono, ME"},
    {"name": "Bowdoin College", "city": "Brunswick, ME"},
    {"name": "Colby College", "city": "Waterville, ME"},
    {"name": "Bates College", "city": "Lewiston, ME"},
    # Maryland
    {"name": "University of Maryland, College Park", "city": "College Park, MD"},
    {"name": "Johns Hopkins University", "city": "Baltimore, MD"},
    {"name": "Towson University", "city": "Towson, MD"},
    {"name": "Loyola University Maryland", "city": "Baltimore, MD"},
    {"name": "University of Maryland, Baltimore County", "city": "Baltimore, MD"},
    {"name": "Morgan State University", "city": "Baltimore, MD"},
    {"name": "United States Naval Academy", "city": "Annapolis, MD"},
    # Massachusetts
    {"name": "Massachusetts Institute of Technology", "city": "Cambridge, MA"},
    {"name": "Harvard University", "city": "Cambridge, MA"},
    {"name": "Boston University", "city": "Boston, MA"},
    {"name": "Boston College", "city": "Chestnut Hill, MA"},
    {"name": "Northeastern University", "city": "Boston, MA"},
    {"name": "Tufts University", "city": "Medford, MA"},
    {"name": "Brandeis University", "city": "Waltham, MA"},
    {"name": "University of Massachusetts Amherst", "city": "Amherst, MA"},
    {"name": "Williams College", "city": "Williamstown, MA"},
    {"name": "Amherst College", "city": "Amherst, MA"},
    {"name": "Smith College", "city": "Northampton, MA"},
    {"name": "Wellesley College", "city": "Wellesley, MA"},
    {"name": "Mount Holyoke College", "city": "South Hadley, MA"},
    {"name": "Worcester Polytechnic Institute", "city": "Worcester, MA"},
    {"name": "Clark University", "city": "Worcester, MA"},
    # Michigan
    {"name": "University of Michigan", "city": "Ann Arbor, MI"},
    {"name": "Michigan State University", "city": "East Lansing, MI"},
    {"name": "Wayne State University", "city": "Detroit, MI"},
    {"name": "Western Michigan University", "city": "Kalamazoo, MI"},
    {"name": "Oakland University", "city": "Rochester, MI"},
    {"name": "Grand Valley State University", "city": "Allendale, MI"},
    {"name": "Central Michigan University", "city": "Mount Pleasant, MI"},
    {"name": "Michigan Technological University", "city": "Houghton, MI"},
    {"name": "Kalamazoo College", "city": "Kalamazoo, MI"},
    # Minnesota
    {"name": "University of Minnesota Twin Cities", "city": "Minneapolis, MN"},
    {"name": "Carleton College", "city": "Northfield, MN"},
    {"name": "Macalester College", "city": "Saint Paul, MN"},
    {"name": "St. Olaf College", "city": "Northfield, MN"},
    {"name": "University of St. Thomas", "city": "Saint Paul, MN"},
    {"name": "Minnesota State University Mankato", "city": "Mankato, MN"},
    # Mississippi
    {"name": "University of Mississippi", "city": "Oxford, MS"},
    {"name": "Mississippi State University", "city": "Starkville, MS"},
    {"name": "Jackson State University", "city": "Jackson, MS"},
    # Missouri
    {"name": "Washington University in St. Louis", "city": "St. Louis, MO"},
    {"name": "University of Missouri", "city": "Columbia, MO"},
    {"name": "Saint Louis University", "city": "St. Louis, MO"},
    {"name": "Missouri University of Science and Technology", "city": "Rolla, MO"},
    {"name": "Truman State University", "city": "Kirksville, MO"},
    # Montana
    {"name": "University of Montana", "city": "Missoula, MT"},
    {"name": "Montana State University", "city": "Bozeman, MT"},
    # Nebraska
    {"name": "University of Nebraska-Lincoln", "city": "Lincoln, NE"},
    {"name": "Creighton University", "city": "Omaha, NE"},
    {"name": "University of Nebraska Omaha", "city": "Omaha, NE"},
    # Nevada
    {"name": "University of Nevada, Las Vegas", "city": "Las Vegas, NV"},
    {"name": "University of Nevada, Reno", "city": "Reno, NV"},
    # New Hampshire
    {"name": "Dartmouth College", "city": "Hanover, NH"},
    {"name": "University of New Hampshire", "city": "Durham, NH"},
    # New Jersey
    {"name": "Princeton University", "city": "Princeton, NJ"},
    {"name": "Rutgers University", "city": "New Brunswick, NJ"},
    {"name": "Stevens Institute of Technology", "city": "Hoboken, NJ"},
    {"name": "Seton Hall University", "city": "South Orange, NJ"},
    {"name": "Rowan University", "city": "Glassboro, NJ"},
    {"name": "New Jersey Institute of Technology", "city": "Newark, NJ"},
    # New Mexico
    {"name": "University of New Mexico", "city": "Albuquerque, NM"},
    {"name": "New Mexico State University", "city": "Las Cruces, NM"},
    # New York
    {"name": "Columbia University", "city": "New York, NY"},
    {"name": "Cornell University", "city": "Ithaca, NY"},
    {"name": "New York University", "city": "New York, NY"},
    {"name": "Fordham University", "city": "New York, NY"},
    {"name": "Syracuse University", "city": "Syracuse, NY"},
    {"name": "University at Buffalo", "city": "Buffalo, NY"},
    {"name": "Stony Brook University", "city": "Stony Brook, NY"},
    {"name": "University at Albany", "city": "Albany, NY"},
    {"name": "Binghamton University", "city": "Binghamton, NY"},
    {"name": "Rensselaer Polytechnic Institute", "city": "Troy, NY"},
    {"name": "Rochester Institute of Technology", "city": "Rochester, NY"},
    {"name": "University of Rochester", "city": "Rochester, NY"},
    {"name": "Vassar College", "city": "Poughkeepsie, NY"},
    {"name": "Barnard College", "city": "New York, NY"},
    {"name": "Colgate University", "city": "Hamilton, NY"},
    {"name": "Hamilton College", "city": "Clinton, NY"},
    {"name": "Skidmore College", "city": "Saratoga Springs, NY"},
    {"name": "Hofstra University", "city": "Hempstead, NY"},
    {"name": "Pace University", "city": "New York, NY"},
    {"name": "St. John's University", "city": "Jamaica, NY"},
    {"name": "Iona University", "city": "New Rochelle, NY"},
    {"name": "Manhattan College", "city": "Riverdale, NY"},
    {"name": "Marist College", "city": "Poughkeepsie, NY"},
    # North Carolina
    {"name": "Duke University", "city": "Durham, NC"},
    {"name": "University of North Carolina at Chapel Hill", "city": "Chapel Hill, NC"},
    {"name": "North Carolina State University", "city": "Raleigh, NC"},
    {"name": "Wake Forest University", "city": "Winston-Salem, NC"},
    {"name": "Davidson College", "city": "Davidson, NC"},
    {"name": "Elon University", "city": "Elon, NC"},
    {"name": "Appalachian State University", "city": "Boone, NC"},
    {"name": "University of North Carolina at Charlotte", "city": "Charlotte, NC"},
    {"name": "East Carolina University", "city": "Greenville, NC"},
    # North Dakota
    {"name": "University of North Dakota", "city": "Grand Forks, ND"},
    {"name": "North Dakota State University", "city": "Fargo, ND"},
    # Ohio
    {"name": "Ohio State University", "city": "Columbus, OH"},
    {"name": "Case Western Reserve University", "city": "Cleveland, OH"},
    {"name": "University of Cincinnati", "city": "Cincinnati, OH"},
    {"name": "Ohio University", "city": "Athens, OH"},
    {"name": "Miami University", "city": "Oxford, OH"},
    {"name": "Bowling Green State University", "city": "Bowling Green, OH"},
    {"name": "Kent State University", "city": "Kent, OH"},
    {"name": "Xavier University", "city": "Cincinnati, OH"},
    {"name": "Denison University", "city": "Granville, OH"},
    {"name": "Oberlin College", "city": "Oberlin, OH"},
    {"name": "College of Wooster", "city": "Wooster, OH"},
    # Oklahoma
    {"name": "University of Oklahoma", "city": "Norman, OK"},
    {"name": "Oklahoma State University", "city": "Stillwater, OK"},
    {"name": "University of Tulsa", "city": "Tulsa, OK"},
    # Oregon
    {"name": "University of Oregon", "city": "Eugene, OR"},
    {"name": "Oregon State University", "city": "Corvallis, OR"},
    {"name": "Portland State University", "city": "Portland, OR"},
    {"name": "Reed College", "city": "Portland, OR"},
    {"name": "Lewis & Clark College", "city": "Portland, OR"},
    {"name": "Willamette University", "city": "Salem, OR"},
    # Pennsylvania
    {"name": "University of Pennsylvania", "city": "Philadelphia, PA"},
    {"name": "Carnegie Mellon University", "city": "Pittsburgh, PA"},
    {"name": "Penn State University", "city": "University Park, PA"},
    {"name": "Temple University", "city": "Philadelphia, PA"},
    {"name": "Drexel University", "city": "Philadelphia, PA"},
    {"name": "Villanova University", "city": "Villanova, PA"},
    {"name": "Lehigh University", "city": "Bethlehem, PA"},
    {"name": "Bucknell University", "city": "Lewisburg, PA"},
    {"name": "Lafayette College", "city": "Easton, PA"},
    {"name": "Swarthmore College", "city": "Swarthmore, PA"},
    {"name": "Haverford College", "city": "Haverford, PA"},
    {"name": "Bryn Mawr College", "city": "Bryn Mawr, PA"},
    {"name": "Dickinson College", "city": "Carlisle, PA"},
    {"name": "Gettysburg College", "city": "Gettysburg, PA"},
    {"name": "University of Pittsburgh", "city": "Pittsburgh, PA"},
    {"name": "Duquesne University", "city": "Pittsburgh, PA"},
    {"name": "Saint Joseph's University", "city": "Philadelphia, PA"},
    # Rhode Island
    {"name": "Brown University", "city": "Providence, RI"},
    {"name": "University of Rhode Island", "city": "Kingston, RI"},
    {"name": "Providence College", "city": "Providence, RI"},
    # South Carolina
    {"name": "University of South Carolina", "city": "Columbia, SC"},
    {"name": "Clemson University", "city": "Clemson, SC"},
    {"name": "Furman University", "city": "Greenville, SC"},
    {"name": "College of Charleston", "city": "Charleston, SC"},
    {"name": "Wofford College", "city": "Spartanburg, SC"},
    # South Dakota
    {"name": "University of South Dakota", "city": "Vermillion, SD"},
    {"name": "South Dakota State University", "city": "Brookings, SD"},
    # Tennessee
    {"name": "Vanderbilt University", "city": "Nashville, TN"},
    {"name": "University of Tennessee", "city": "Knoxville, TN"},
    {"name": "Rhodes College", "city": "Memphis, TN"},
    {"name": "Belmont University", "city": "Nashville, TN"},
    {"name": "Middle Tennessee State University", "city": "Murfreesboro, TN"},
    {"name": "Tennessee Tech University", "city": "Cookeville, TN"},
    # Texas
    {"name": "University of Texas at Austin", "city": "Austin, TX"},
    {"name": "Texas A&M University", "city": "College Station, TX"},
    {"name": "Rice University", "city": "Houston, TX"},
    {"name": "Southern Methodist University", "city": "Dallas, TX"},
    {"name": "Texas Christian University", "city": "Fort Worth, TX"},
    {"name": "Baylor University", "city": "Waco, TX"},
    {"name": "Texas Tech University", "city": "Lubbock, TX"},
    {"name": "University of Houston", "city": "Houston, TX"},
    {"name": "University of North Texas", "city": "Denton, TX"},
    {"name": "University of Texas at Dallas", "city": "Richardson, TX"},
    {"name": "University of Texas at San Antonio", "city": "San Antonio, TX"},
    {"name": "Texas State University", "city": "San Marcos, TX"},
    {"name": "Trinity University", "city": "San Antonio, TX"},
    {"name": "United States Air Force Academy", "city": "Colorado Springs, CO"},
    # Utah
    {"name": "University of Utah", "city": "Salt Lake City, UT"},
    {"name": "Brigham Young University", "city": "Provo, UT"},
    {"name": "Utah State University", "city": "Logan, UT"},
    {"name": "Weber State University", "city": "Ogden, UT"},
    # Vermont
    {"name": "University of Vermont", "city": "Burlington, VT"},
    {"name": "Middlebury College", "city": "Middlebury, VT"},
    # Virginia
    {"name": "University of Virginia", "city": "Charlottesville, VA"},
    {"name": "Virginia Tech", "city": "Blacksburg, VA"},
    {"name": "College of William & Mary", "city": "Williamsburg, VA"},
    {"name": "George Mason University", "city": "Fairfax, VA"},
    {"name": "James Madison University", "city": "Harrisonburg, VA"},
    {"name": "Virginia Commonwealth University", "city": "Richmond, VA"},
    {"name": "Washington and Lee University", "city": "Lexington, VA"},
    {"name": "United States Military Academy", "city": "West Point, NY"},
    {"name": "Hampden-Sydney College", "city": "Farmville, VA"},
    {"name": "University of Richmond", "city": "Richmond, VA"},
    # Washington
    {"name": "University of Washington", "city": "Seattle, WA"},
    {"name": "Washington State University", "city": "Pullman, WA"},
    {"name": "Seattle University", "city": "Seattle, WA"},
    {"name": "Gonzaga University", "city": "Spokane, WA"},
    {"name": "Whitman College", "city": "Walla Walla, WA"},
    {"name": "Western Washington University", "city": "Bellingham, WA"},
    # Washington D.C.
    {"name": "Georgetown University", "city": "Washington, DC"},
    {"name": "George Washington University", "city": "Washington, DC"},
    {"name": "American University", "city": "Washington, DC"},
    {"name": "Howard University", "city": "Washington, DC"},
    {"name": "Catholic University of America", "city": "Washington, DC"},
    # West Virginia
    {"name": "West Virginia University", "city": "Morgantown, WV"},
    {"name": "Marshall University", "city": "Huntington, WV"},
    # Wisconsin
    {"name": "University of Wisconsin-Madison", "city": "Madison, WI"},
    {"name": "Marquette University", "city": "Milwaukee, WI"},
    {"name": "University of Wisconsin-Milwaukee", "city": "Milwaukee, WI"},
    {"name": "Lawrence University", "city": "Appleton, WI"},
    {"name": "Beloit College", "city": "Beloit, WI"},
    # Wyoming
    {"name": "University of Wyoming", "city": "Laramie, WY"},
]


def seed():
    db = SessionLocal()
    try:
        new_count = 0
        for college in COLLEGES:
            exists = db.query(College).filter_by(name=college["name"]).first()
            if not exists:
                db.add(College(**college))
                new_count += 1
        db.commit()
        print(f"Done — {new_count} new colleges added, {len(COLLEGES) - new_count} already existed.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()