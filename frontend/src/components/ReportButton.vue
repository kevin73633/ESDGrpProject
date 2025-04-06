<template>
  <div>
    <button @click="fetchDealDetails" class="report-button" :disabled="isLoading">
      <span v-if="isLoading" class="loading-spinner"></span>
      <span v-else class="report-icon">⚠️</span> Report
    </button>

    <!-- Modal -->
    <div v-if="showModal" class="modal-backdrop">
      <div class="modal-content">
        <h2>Report User</h2>
        <p>Are you sure you want to report this user?</p>
        
        <div class="form-group">
          <label for="reason">Reason:</label>
          <select v-model="reason" id="reason" required>
            <option value="" disabled>Select a reason</option>
            <option value="Inappropriate Content">Inappropriate Content</option>
            <option value="Harassment">Harassment</option>
            <option value="Spam">Spam</option>
            <option value="Scam">Scam</option>
            <option value="Other">Other</option>
          </select>
        </div>
        
        <div v-if="reason === 'Other'" class="form-group">
          <label for="otherReason">Please specify:</label>
          <textarea v-model="otherReasonText" id="otherReason" rows="3"></textarea>
        </div>
        
        <div class="modal-actions">
          <button @click="closeModal" class="cancel-button">Cancel</button>
          <button @click="confirmReport" class="confirm-button" :disabled="!isReasonValid">
            Confirm Report
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const DEAL_API_URL = 'http://localhost:8000'; 
const REPORT_USER_API_URL = 'http://localhost:8000/report_user'; 
import axios from 'axios';
export default {
  name: 'ReportButton',
  props: {
    reportedUserId: {
      type: String,
      required: true
    },
    currentUserId: {
      type: String,
      required: true
    },
    dealId: {
      type: [Number, String],
      required: true
    },
  },
  data() {
    return {
      isLoading: false,
      showModal: false,
      reason: '',
      otherReasonText: '',
      isSubmitting: false
    }
  },
  computed: {
    isReasonValid() {
      return this.reason && (this.reason !== 'Other' || this.otherReasonText.trim().length > 0);
    },
    finalReason() {
      return this.reason === 'Other' ? this.otherReasonText : this.reason;
    }
  },
  methods: {
    async fetchDealDetails() {
          this.isLoading = true;
          try {
            this.showModal = true;
            this.loadingDetails = true;
            this.error = null;
            this.showComplaintForm = false;
            this.termsAccepted = false;
            this.userRating = 0;
            this.ratingFeedback = '';
  
            const dealResponse = await fetch(`${DEAL_API_URL}/deal/${this.dealId}`);
            
            if (!dealResponse.ok) {
              throw new Error(`HTTP Error ${dealResponse.status}`);
            }
  
            const contentType = dealResponse.headers.get("content-type");
            if (!contentType || !contentType.includes("application/json")) {
              throw new Error("Expected JSON, received HTML or another format.");
            }
  
            const dealData = await dealResponse.json();
            console.log("Deal Data:", dealData); // Debugging
            this.dealDetails = dealData.data;
  
          } catch (error) {
            console.error('Error fetching deal details:', error);
            this.error = error.message || "An unexpected error occurred.";
          } finally {
            this.loadingDetails = false;
            this.isLoading = false;
          }
        },
    closeModal() {
      this.showModal = false;
      this.reason = '';
      this.otherReasonText = '';
    },
    async confirmReport() {
      if (!this.isReasonValid || this.isSubmitting) return;
      
      this.isSubmitting = true;
      
      try {
        // API call to submit the report
        const response = await axios.post(`${REPORT_USER_API_URL}`, {
          UserID: this.currentUserId,
            ReportedUserID: this.reportedUserId,
            dealId: this.dealId,
            Reason: this.finalReason,
            });
        
            if (response.data.code === 200) {
          // Emit an event with report data before closing the modal
          this.$emit('report-submitted', {
            ...response.data,
            dealId: this.dealId,
            // Include this flag to indicate immediate UI update needed
            immediateUpdate: true 
          });
          
          this.closeModal();
          this.$emit('show-notification', {
            message: 'Report submitted successfully',
            type: 'success'
          });
        } else {
          throw new Error('Failed to submit report');
        }
      } catch (error) {
        console.error('Error submitting report:', error);
        this.$emit('show-notification', {
          message: 'Failed to submit report. Please try again.',
          type: 'error'
        });
      } finally {
        this.isSubmitting = false;
      }
    }
  }
}
</script>

<style scoped>
.report-button {
  background-color: #ff5252;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  font-weight: bold;
}

.report-icon {
  margin-right: 6px;
}

.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  padding: 24px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-weight: bold;
}

.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.cancel-button {
  background-color: #e0e0e0;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-button {
  background-color: #ff5252;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.confirm-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}
</style>