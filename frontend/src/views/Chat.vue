<template>
    <div class="chat-container">
      <h2>Chat with {{ otherParty }}</h2>
      <!-- Chat Messages Section -->
      <div class="chat-messages">
        <!-- Display chat messages here -->
      </div>
  
      <!-- Action Buttons -->
      <div class="action-buttons">
        <button @click="confirmDeal">Confirm Deal</button>
        <button @click="verifyDeal">Verify Deal</button>
        <button @click="reportIssue">Report Issue</button>
      </div>
  
      <!-- Modal for Review/Rating -->
      <div v-if="showReviewModal" class="modal">
        <h3>Leave a Review</h3>
        <textarea v-model="reviewText" placeholder="Write your review here..."></textarea>
        <label for="rating">Rating: </label>
        <select v-model="rating">
          <option value="1">1</option>
          <option value="2">2</option>
          <option value="3">3</option>
          <option value="4">4</option>
          <option value="5">5</option>
        </select>
        <button @click="submitReview">Submit Review</button>
        <button @click="closeModal">Close</button>
      </div>
  
      <!-- Modal for Reporting -->
      <div v-if="showReportModal" class="modal">
        <h3>Report an Issue</h3>
        <textarea v-model="reportText" placeholder="Describe the issue..."></textarea>
        <button @click="submitReport">Submit Report</button>
        <button @click="closeModal">Close</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: ['dealId'],
    data() {
      return {
        otherParty: 'John Doe',  // Replace with dynamic user info
        showReviewModal: false,
        showReportModal: false,
        reviewText: '',
        rating: 5,
        reportText: '',
      };
    },
    methods: {
      confirmDeal() {
        // Handle deal confirmation logic here
        console.log("Deal Confirmed");
      },
      verifyDeal() {
        // Show review modal
        this.showReviewModal = true;
      },
      reportIssue() {
        // Show report modal
        this.showReportModal = true;
      },
      submitReview() {
        // Submit the review and rating (you can send it to a server or store locally)
        console.log(`Review: ${this.reviewText}, Rating: ${this.rating}`);
        this.closeModal();  // Close the modal after submission
      },
      submitReport() {
        // Submit the report (you can send it to a server or store locally)
        console.log(`Report: ${this.reportText}`);
        this.closeModal();  // Close the modal after submission
      },
      closeModal() {
        this.showReviewModal = false;
        this.showReportModal = false;
      },
    },
  };
  </script>
  
  <style scoped>
  /* Basic styles for the chat and modals */
  .chat-container {
    padding: 20px;
  }
  .chat-messages {
    border-bottom: 1px solid #ddd;
    padding-bottom: 10px;
    margin-bottom: 10px;
  }
  .action-buttons button {
    margin: 5px;
  }
  .modal {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
  }
  .modal div {
    background: white;
    padding: 20px;
    border-radius: 5px;
  }
  </style>
  