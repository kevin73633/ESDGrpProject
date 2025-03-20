<template>
  <div class="messaging-app">
    <!-- Main container with sidebar and content -->
    <div class="container-fluid p-0">
      <div class="row g-0">
        <!-- Sidebar / Conversations list -->
        <div class="col-md-3 border-end" style="height: 100vh; overflow: hidden;">
          <div class="d-flex flex-column h-100">
            <!-- Header with back button -->
            <div class="p-3 border-bottom">
              <div class="d-flex align-items-center">
                <button class="btn btn-sm me-3">
                  <i class="fas fa-arrow-left"></i>
                </button>
                <h6 class="mb-0">Conversations</h6>
              </div>
            </div>
            
            <!-- Conversations list -->
            <div class="overflow-auto flex-grow-1">
              <ul class="list-unstyled mb-0">
                <li v-for="user in users" :key="user.id" class="p-3 border-bottom position-relative">
                  <a href="#" class="d-flex text-decoration-none text-dark">
                    <div class="position-relative me-3">
                      <div class="bg-secondary rounded-circle" style="width: 45px; height: 45px; display: flex; align-items: center; justify-content: center;">
                        <span class="text-white">{{ user.name.charAt(0) }}</span>
                      </div>
                      <span v-if="user.status" class="position-absolute bottom-0 end-0 badge rounded-pill" :class="user.status"></span>
                    </div>
                    <div class="flex-grow-1">
                      <div class="d-flex justify-content-between">
                        <p class="fw-bold mb-0">{{ user.name }}</p>
                        <p class="small text-muted">{{ user.time }}</p>
                      </div>
                      <p class="small text-muted text-truncate mb-0" style="max-width: 160px;">{{ user.message }}</p>
                    </div>
                  </a>
                </li>
              </ul>
            </div>
          </div>
        </div>
        
        <!-- Main content area -->
        <div class="col-md-9 d-flex flex-column" style="height: 100vh; overflow: hidden;">
          <!-- Header with user info -->
          <div class="p-3 border-bottom">
            <div class="d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <div class="position-relative me-2">
                  <img src="/api/placeholder/40/40" alt="avatar" class="rounded-circle" width="40">
                </div>
                <div>
                  <p class="fw-bold mb-0">Name</p>
                </div>
              </div>
              <div>
                <button class="btn btn-sm btn-light me-2">
                  <i class="fas fa-bell"></i>
                </button>
                <button class="btn btn-sm btn-light">
                  <i class="fas fa-cog"></i>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Chat content area (scrollable) -->
          <div class="flex-grow-1 overflow-auto p-3" id="chat-content">
            <!-- Deal card -->
            <div class="card mb-3">
              <div class="card-body position-relative">
                <div class="d-flex align-items-center mb-3">
                  <div class="bg-light rounded-circle me-3 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                    <span>A</span>
                  </div>
                  <div>
                    <p class="mb-0">&lt;Deal name&gt;</p>
                    <p class="text-muted small mb-0">&lt;Date&gt;</p>
                  </div>
                  <div class="position-absolute top-0 end-0 m-3">
                    <button @click="showReportDialog" class="btn btn-outline-secondary btn-sm">Report</button>
                  </div>
                </div>
                
                <div class="card bg-light">
                  <div class="card-body d-flex align-items-center">
                    <div class="me-3">
                      <div class="bg-white p-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                        <i class="far fa-file"></i>
                      </div>
                    </div>
                    <div class="flex-grow-1">
                      <p class="mb-0">Title</p>
                      <p class="text-muted small mb-0">Description</p>
                    </div>
                    <div class="text-muted small">
                      9:41 AM
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Confirm Deal Button -->
            <div class="mb-4">
              <button @click="showDealConfirmation" class="btn btn-primary">Confirm Deal</button>
            </div>
            
            <!-- Chat bubbles -->
            <div v-for="(message, index) in messages" :key="message.id" class="mb-3">
              <!-- Sent messages (by user) -->
              <div v-if="message.sent" class="d-flex justify-content-end">
                <div class="bg-primary p-3 rounded-3 text-white" style="max-width: 80%;">
                  <p class="mb-0">{{ message.text }}</p>
                  <p class="text-end mb-0 mt-1">
                    <small class="opacity-75">{{ message.time || 'now' }}</small>
                  </p>
                </div>
              </div>
              
              <!-- Received messages -->
              <div v-else class="d-flex">
                <div class="bg-light rounded-circle me-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px; min-width: 40px;">
                  <span>A</span>
                </div>
                <div class="bg-light p-3 rounded-3" style="max-width: 80%;">
                  <p class="mb-0">{{ message.text }}</p>
                  <p class="mb-0 mt-1">
                    <small class="text-muted">{{ message.time || 'now' }}</small>
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Quick responses -->
            <div class="d-flex justify-content-end flex-wrap gap-2 mb-4">
              <button @click="sendQuickReply('Let\'s do it')" class="btn btn-light rounded-pill">Let's do it</button>
              <button @click="sendQuickReply('Great!')" class="btn btn-light rounded-pill">Great!</button>
              <button @click="sendQuickReply('Sounds good')" class="btn btn-light rounded-pill">Sounds good</button>
            </div>
          </div>
          
          <!-- Message input (fixed at bottom) with padding -->
          <div class="p-3 pb-4 border-top mt-auto">
            <form @submit.prevent="sendMessage" class="w-100">
              <div class="input-group">
                <input 
                  v-model="newMessage" 
                  type="text" 
                  class="form-control border" 
                  placeholder="Type a message" 
                  :class="{ 'is-invalid': validationError }"
                >
                <button 
                  type="submit" 
                  class="btn btn-primary border d-flex align-items-center justify-content-center"
                >
                  <i class="fas fa-paper-plane me-2"></i>
                  Send
                </button>
              </div>
              <div v-if="validationError" class="invalid-feedback d-block">
                {{ validationError }}
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Deal Confirmation Modal -->
    <div v-if="showConfirmationModal" class="modal-backdrop fade show"></div>
    <div v-if="showConfirmationModal" class="modal fade show d-block" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Confirm Deal Details</h5>
            <button @click="closeModal" type="button" class="btn-close" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div class="card mb-3">
              <div class="card-body">
                <h6 class="card-title">Deal Information</h6>
                <div class="mb-2">
                  <strong>Deal ID:</strong> {{ dealDetails.id }}
                </div>
                <div class="mb-2">
                  <strong>Name:</strong> {{ dealDetails.name }}
                </div>
                <div class="mb-2">
                  <strong>Date:</strong> {{ dealDetails.date }}
                </div>
                <div class="mb-2">
                  <strong>Amount:</strong> ${{ dealDetails.amount.toFixed(2) }}
                </div>
                <div class="mb-2">
                  <strong>Status:</strong> <span class="badge" :class="getStatusBadgeClass()">{{ dealDetails.status }}</span>
                </div>
                <div class="mb-2">
                  <strong>Description:</strong> {{ dealDetails.description }}
                </div>
                <div class="mb-2">
                  <strong>Parties:</strong> {{ dealDetails.parties.join(', ') }}
                </div>
              </div>
            </div>
            
            <div class="alert alert-info">
              <i class="fas fa-info-circle me-2"></i> Once confirmed, this deal cannot be modified.
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closeModal" type="button" class="btn btn-secondary">Cancel</button>
            <button @click="confirmDeal" type="button" class="btn btn-primary">Confirm Deal</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Report Dialog -->
    <div v-if="showReportModal" class="modal-backdrop fade show"></div>
    <div v-if="showReportModal" class="modal fade show d-block" tabindex="-1" role="dialog" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Report Issue</h5>
            <button @click="showReportModal = false" type="button" class="btn-close" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form>
              <div class="mb-3">
                <label for="reportType" class="form-label">Issue Type</label>
                <select id="reportType" class="form-select" v-model="reportData.type">
                  <option value="">Select an issue type</option>
                  <option value="incorrect_info">Incorrect Information</option>
                  <option value="fraud">Potential Fraud</option>
                  <option value="incomplete">Incomplete Details</option>
                  <option value="other">Other</option>
                </select>
              </div>
              <div class="mb-3">
                <label for="reportDescription" class="form-label">Description</label>
                <textarea 
                  id="reportDescription" 
                  class="form-control" 
                  rows="4" 
                  placeholder="Please provide details about the issue"
                  v-model="reportData.description"
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button @click="showReportModal = false" type="button" class="btn btn-secondary">Cancel</button>
            <button @click="submitReport" type="button" class="btn btn-danger">Submit Report</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      users: [
        { 
          id: 1, 
          name: "Name", 
          message: "Supporting line text lorem ipsum dolor sit amet", 
          time: "10 min", 
          status: "bg-success" 
        },
        { 
          id: 2, 
          name: "Name", 
          message: "Supporting line text lorem ipsum dolor sit amet", 
          time: "10 min", 
          status: "bg-success" 
        },
        { 
          id: 3, 
          name: "Name", 
          message: "Supporting line text lorem ipsum dolor sit amet", 
          time: "10 min", 
          status: "bg-success" 
        },
        { 
          id: 4, 
          name: "Name", 
          message: "Supporting line text lorem ipsum dolor sit amet", 
          time: "10 min", 
          status: "bg-success" 
        },
        { 
          id: 5, 
          name: "Name", 
          message: "Supporting line text lorem ipsum dolor sit amet", 
          time: "10 min", 
          status: "bg-success" 
        },
        { 
          id: 6, 
          name: "Name", 
          message: "Supporting line text lorem ipsum dolor sit amet", 
          time: "10 min", 
          status: "bg-success" 
        },
        { 
          id: 7, 
          name: "Name", 
          message: "Supporting line text lorem ipsum dolor sit amet", 
          time: "10 min", 
          status: "bg-success" 
        },
        { 
          id: 8, 
          name: "Name", 
          message: "Supporting line text lorem ipsum dolor sit amet", 
          time: "10 min", 
          status: "bg-success" 
        }
      ],
      messages: [
        { id: 1, text: "that looks so good!", sent: false, time: "10:25 AM" },
        { id: 2, text: "or we could make this?", sent: true, time: "10:26 AM" }
      ],
      newMessage: "",
      validationError: "",
      showConfirmationModal: false,
      showReportModal: false,
      dealConfirmed: false,
      // Hardcoded deal details (replace with API call later)
      dealDetails: {
        id: "DEAL-2025-03-042",
        name: "Homemade Dumplings Partnership",
        date: "March 20, 2025",
        amount: 2500.00,
        status: "Pending Confirmation",
        description: "Partnership agreement for distribution of homemade dumplings",
        parties: ["Dumpling Co.", "Food Distributors Inc."]
      },
      reportData: {
        type: "",
        description: ""
      }
    };
  },
  methods: {
    sendMessage() {
      // Validate message content
      if (!this.newMessage.trim()) {
        this.validationError = "Please enter a message";
        return;
      }
      
      // Clear validation error
      this.validationError = "";
      
      // Create a new message
      const newMsg = {
        id: Date.now(),
        text: this.newMessage,
        sent: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      // Add to messages array
      this.messages.push(newMsg);
      
      // Clear input
      this.newMessage = "";
      
      // Simulate reply after a short delay (remove this in production)
      if (Math.random() > 0.5) {
        setTimeout(() => {
          const replyMsg = {
            id: Date.now(),
            text: "Thanks for your message!",
            sent: false,
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
          };
          this.messages.push(replyMsg);
        }, 1000);
      }
    },
    sendQuickReply(text) {
      const quickReply = {
        id: Date.now(),
        text: text,
        sent: true,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      
      this.messages.push(quickReply);
      
      // Simulate response
      setTimeout(() => {
        const response = {
          id: Date.now(),
          text: "Great! I'll update our records.",
          sent: false,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        this.messages.push(response);
      }, 800);
    },
    showDealConfirmation() {
      // In a real app, you would fetch the latest deal details here
      // this.fetchDealDetails(dealId);
      
      // For demo, we'll just show the modal with hardcoded data
      this.showConfirmationModal = true;
    },
    closeModal() {
      this.showConfirmationModal = false;
    },
    confirmDeal() {
      // In a real app, send confirmation to your API
      // const response = await this.api.confirmDeal(this.dealDetails.id);
      
      // For demo, we'll simulate a successful confirmation
      this.dealDetails.status = "Confirmed";
      this.dealConfirmed = true;
      
      // Close the modal
      this.showConfirmationModal = false;
      
      // Add confirmation message to chat
      this.messages.push({
        id: Date.now(),
        text: "Deal has been confirmed successfully! 🎉",
        sent: false,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      });
    },
    showReportDialog() {
      this.showReportModal = true;
      this.reportData = {
        type: "",
        description: ""
      };
    },
    submitReport() {
      // Validate report data
      if (!this.reportData.type || !this.reportData.description.trim()) {
        alert("Please fill in all report fields");
        return;
      }
      
      // In a real app, send report to your API
      // const response = await this.api.submitReport(this.dealDetails.id, this.reportData);
      
      // Close the modal
      this.showReportModal = false;
      
      // Show confirmation message
      alert("Your report has been submitted. Our team will review it shortly.");
    },
    getStatusBadgeClass() {
      // Return appropriate badge class based on status
      const statusMap = {
        "Confirmed": "bg-success",
        "Pending Confirmation": "bg-warning",
        "Rejected": "bg-danger",
        "Cancelled": "bg-secondary"
      };
      
      return statusMap[this.dealDetails.status] || "bg-primary";
    },
    scrollToBottom() {
      const chatContent = document.getElementById('chat-content');
      if (chatContent) {
        chatContent.scrollTop = chatContent.scrollHeight;
      }
    },
    // This method will be implemented later to fetch deal details from your API
    async fetchDealDetails(dealId) {
      try {
        // Replace with actual API call
        // const response = await fetch(`/api/deals/${dealId}`);
        // this.dealDetails = await response.json();
        console.log("Would fetch details for deal ID:", dealId);
      } catch (error) {
        console.error("Error fetching deal details:", error);
      }
    }
  },
  mounted() {
    // Scroll to bottom of chat on load
    this.scrollToBottom();
  },
  updated() {
    // Scroll to bottom of chat when messages update
    this.scrollToBottom();
  },
  created() {
    // Add bottom padding for mobile screens
    if (window.innerWidth <= 768) {
      document.documentElement.style.setProperty('--safe-bottom-padding', '20px');
    }
  },
  watch: {
    // Clear validation error when user starts typing
    newMessage(val) {
      if (val && this.validationError) {
        this.validationError = "";
      }
    }
  }
};
</script>

<style>
.messaging-app {
  height: 100vh;
  overflow: hidden;
}

.badge-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.bg-success { 
  background-color: green !important; 
}

.bg-warning { 
  background-color: orange !important; 
}

.bg-danger { 
  background-color: red !important; 
}

.invalid-feedback {
  display: block;
  margin-top: 0.25rem;
  font-size: 0.875em;
  color: #dc3545;
}

.is-invalid {
  border-color: #dc3545 !important;
}

/* Modal backdrop styles */
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1040;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1050;
  width: 100%;
  height: 100%;
  overflow-x: hidden;
  overflow-y: auto;
  outline: 0;
}

.modal-dialog {
  position: relative;
  margin: 1.75rem auto;
  max-width: 500px;
}

.fade {
  transition: opacity 0.15s linear;
}

.fade.show {
  opacity: 1;
}

/* For mobile screens, adjust the height */
@media (max-width: 768px) {
  .col-md-3, .col-md-9 {
    height: auto !important;
  }
  
  .messaging-app {
    display: flex;
    flex-direction: column;
  }
  
  #chat-content {
    max-height: calc(100vh - 150px); /* Increased to account for extra bottom padding */
  }
  
  .pb-4 {
    padding-bottom: 1.8rem !important; /* Extra padding at the bottom of the input */
  }
  
  .modal-dialog {
    margin: 0.5rem;
    max-width: calc(100% - 1rem);
  }
}

/* Custom scrollbar styles */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>