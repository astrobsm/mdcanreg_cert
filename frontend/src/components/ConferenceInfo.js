import React from 'react';

const ConferenceInfo = () => {
  return (
    <div className="conference-info-container">
      <section className="sub-themes-section">
        <h2 className="section-title">Sub-themes</h2>
        <ul className="sub-themes-list">
          <li>Medical migration syndrome: fortune and misfortunes</li>
          <li>Physician heal thyself: The mismatch between knowledge and practice</li>
        </ul>
      </section>

      <section className="program-events-section">
        <h2 className="section-title">Programme of Events</h2>
        
        <div className="day-schedule">
          <h3 className="day-title">Monday 1st Sept 2025</h3>
          <ul className="event-list">
            <li><span className="event-name">Arrival of NOC</span><span className="event-time">All day</span></li>
            <li><span className="event-name">NOC ‑ LOC Meeting</span><span className="event-time">7 pm</span></li>
          </ul>
        </div>

        <div className="day-schedule">
          <h3 className="day-title">Tuesday 2nd Sept 2025</h3>
          <ul className="event-list">
            <li><span className="event-name">Courtesy visits</span><span className="event-time">All day</span></li>
            <li><span className="event-name">Arrival of delegates</span><span className="event-time">All day</span></li>
            <li><span className="event-name">Medical outreach</span><span className="event-time">All day</span></li>
            <li><span className="event-name">Welcome, cocktail</span><span className="event-time">7 pm</span></li>
          </ul>
        </div>

        <div className="day-schedule">
          <h3 className="day-title">Wednesday 3rd Sept 2025</h3>
          <ul className="event-list">
            <li><span className="event-name">Registration</span><span className="event-time">7 ‑ 8 am</span></li>
            <li><span className="event-name">First Scientific session</span><span className="event-time">8 ‑ 10:30 am</span></li>
            <li><span className="event-name">Tea Break</span><span className="event-time">10:30 ‑ 11 am</span></li>
            <li><span className="event-name">Second session</span><span className="event-time">11 am ‑ 12 noon</span></li>
            <li><span className="event-name">Sub‑theme lecture</span><span className="event-time">12 ‑ 1:30 pm</span></li>
            <li><span className="event-name">Lunch</span><span className="event-time">1:30 ‑ 2:30 pm</span></li>
            <li><span className="event-name">NEC 1</span><span className="event-time">3 ‑ 5 pm</span></li>
          </ul>
        </div>

        <div className="day-schedule">
          <h3 className="day-title">Thursday 4th Sept 2025</h3>
          <ul className="event-list">
            <li><span className="event-name">Registration</span><span className="event-time">7 ‑ 8 am</span></li>
            <li><span className="event-name">Third session</span><span className="event-time">8 ‑ 9:30 am</span></li>
            <li><span className="event-name">Tea Break</span><span className="event-time">10 ‑ 11 am</span></li>
            <li><span className="event-name">Opening Ceremony</span><span className="event-time">11 am ‑ 1 pm</span></li>
            <li><span className="event-name">Theme lecture</span><span className="event-time">11:45 am ‑ 12:30 pm</span></li>
            <li><span className="event-name">Lunch</span><span className="event-time">1 ‑ 2 pm</span></li>
            <li><span className="event-name">Product Presentation</span><span className="event-time">2 ‑ 2:30 pm</span></li>
            <li><span className="event-name">NEC 2</span><span className="event-time">3 ‑ 5 pm</span></li>
          </ul>
        </div>

        <div className="day-schedule">
          <h3 className="day-title">Friday 5th Sept 2025</h3>
          <ul className="event-list">
            <li><span className="event-name">Sub‑theme lecture</span><span className="event-time">9:30 ‑ 10:15 am</span></li>
            <li><span className="event-name">Tea Break</span><span className="event-time">10:15 ‑ 11 am</span></li>
            <li><span className="event-name">Product Presentation</span><span className="event-time">11 ‑ 11:30 am</span></li>
            <li><span className="event-name">Lunch/Prayers</span><span className="event-time">11:30 ‑ 2 pm</span></li>
            <li><span className="event-name">BDM & Election, Dinner</span><span className="event-time">Evening</span></li>
          </ul>
        </div>

        <div className="day-schedule">
          <h3 className="day-title">Saturday 6th Sept 2025</h3>
          <ul className="event-list">
            <li><span className="event-name">Press Conference</span><span className="event-time">Morning</span></li>
            <li><span className="event-name">Departure!</span><span className="event-time">All day</span></li>
          </ul>
        </div>
      </section>
    </div>
  );
};

export default ConferenceInfo;
