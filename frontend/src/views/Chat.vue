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
                <button class="btn btn-link text-dark me-3 p-0" @click="goBack" style="font-size: 1.5rem;">
                  <i class="bi bi-arrow-left"></i>
                </button>
                <h6 class="mb-0">Conversations</h6>
              </div>
            </div>
            
            <!-- Conversations list -->
            <div class="overflow-auto flex-grow-1">
              <div v-if="isLoading" class="text-center p-4">
                <div class="spinner-border text-primary" role="status">
                  <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading conversations...</p>
              </div>
              
              <div v-else-if="apiError" class="alert alert-danger m-3">
                {{ apiError }}
                <button @click="initializeChats" class="btn btn-outline-danger btn-sm mt-2">Retry</button>
              </div>
              
              <div v-else-if="chatUsers.length === 0" class="text-center p-4">
                <p class="text-muted">No conversations yet</p>
              </div>
              
              <ul v-else class="list-unstyled mb-0">
                <li 
                  v-for="user in chatUsers" 
                  :key="user.uid" 
                  class="p-3 border-bottom position-relative"
                  :class="{'bg-light': user.active}"
                  @click="selectChat(user.uid)"
                  style="cursor: pointer;"
                >
                  <div class="d-flex text-decoration-none text-dark">
                    <div class="position-relative me-3">
                      <div class="bg-secondary rounded-circle" style="width: 45px; height: 45px; display: flex; align-items: center; justify-content: center;">
                        <span class="text-white">{{ user.name.charAt(0) }}</span>
                      </div>
                      <span v-if="user.online" class="position-absolute bottom-0 end-0 badge rounded-pill bg-success"></span>
                    </div>
                    <div class="flex-grow-1">
                      <div class="d-flex justify-content-between">
                        <p class="fw-bold mb-0">{{ user.name }}</p>
                        <p class="small text-muted">{{ user.lastMessageTime || '' }}</p>
                      </div>
                      <p class="small text-muted text-truncate mb-0" style="max-width: 160px;">{{ user.lastMessage || 'No messages yet' }}</p>
                    </div>
                  </div>
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
                  <p class="fw-bold mb-0">{{ selectedChatUser ? selectedChatUser.name : 'No chat selected' }}</p>
                </div>
              </div>
              <div>
                <!-- IMPLEMENT REPORT FUNCTIONALITY pls -->
                <button class="btn btn-sm btn-light" >
                  Report
                </button>
                <button class="btn btn-sm btn-light me-2">
                  <i class="bi bi-bell"></i>
                </button>
                <button class="btn btn-sm btn-light" @click="goToProfile">
                  <i class="bi bi-cog">profile</i>
                </button>
              </div>
            </div>
          </div>
          
          <!-- Chat content area (scrollable) -->
          <div ref="chatContent" class="flex-grow-1 overflow-auto p-3" id="chat-content">
            <!-- Deal Confirmation Banner (when confirmed) -->
            <div v-if="dealConfirmed" class="alert alert-success mb-3 d-flex align-items-center">
              <i class="fas fa-check-circle me-2 fs-5"></i>
              <div>
                <strong>Deal Confirmed!</strong> 
                <p class="mb-0 small">This deal has been confirmed and is now active.</p>
              </div>
              <div class="ms-auto">
                <span class="badge bg-success">Confirmed</span>
              </div>
            </div>
          
            <!-- Deal card (if applicable) -->
            <div class="card mb-3" v-if="dealDetails.id">
              <div class="card-body position-relative">
                <div class="d-flex align-items-center mb-3">
                  <div class="bg-light rounded-circle me-3 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                    <span>{{ dealDetails.name ? dealDetails.name.charAt(0) : 'D' }}</span>
                  </div>
                  <div>
                    <p class="mb-0">{{ dealDetails.name || '<Deal name>' }}</p>
                    <p class="text-muted small mb-0">{{ dealDetails.date || '<Date>' }}</p>
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
                      <p class="mb-0">{{ dealDetails.description ? dealDetails.description.split(' ').slice(0, 3).join(' ') : 'Title' }}</p>
                      <p class="text-muted small mb-0">{{ dealDetails.description || 'Description' }}</p>
                    </div>
                    <div class="text-muted small">
                      {{ dealDetails.date ? formatShortTime(dealDetails.date) : '' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Confirm/Verify Deal Button (if applicable) -->
            <div class="mb-4" v-if="dealDetails.id">
              <button 
                @click="dealConfirmed ? verifyDeal() : showDealConfirmation()" 
                class="btn" 
                :class="dealConfirmed ? 'btn-success' : 'btn-primary'"
              >
                <i :class="dealConfirmed ? 'fas fa-check-double me-2' : 'fas fa-check me-2'"></i>
                {{ dealConfirmed ? 'Verify Deal' : 'Confirm Deal' }}
              </button>
            </div>
            
            <!-- Chat bubbles -->
            <div v-for="(message, index) in messages" :key="message.messageid" class="mb-3">
              <!-- Sent messages (by current user) -->
              <div v-if="message.senderid === currentUserId" class="d-flex justify-content-end">
                <div class="bg-primary p-3 rounded-3 text-white" style="max-width: 80%;">
                  <p class="mb-0">{{ message.message }}</p>
                  <p class="text-end mb-0 mt-1">
                    <small class="opacity-75">{{ formatMessageTime(message.sentat) }}</small>
                  </p>
                </div>
              </div>
              
              <!-- Received messages -->
              <div v-else class="d-flex">
                <div class="bg-light rounded-circle me-2 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px; min-width: 40px;">
                  <span>{{ selectedChatUser ? selectedChatUser.name.charAt(0) : 'A' }}</span>
                </div>
                <div class="bg-light p-3 rounded-3" style="max-width: 80%;">
                  <p class="mb-0">{{ message.message }}</p>
                  <p class="mb-0 mt-1">
                    <small class="text-muted">{{ formatMessageTime(message.sentat) }}</small>
                  </p>
                </div>
              </div>
            </div>
            
            <!-- Quick responses -->
            <div class="d-flex justify-content-end flex-wrap gap-2 mb-4">
              <button v-for="(reply, index) in quickReplies" :key="index" @click="sendQuickReply(reply)" class="btn btn-light rounded-pill">
                {{ reply }}
              </button>
            </div>
          </div>
          
          <!-- Message input (fixed at bottom) with padding -->
          <div class="p-3 pb-4 border-top mt-auto">
            <button class="btn btn-sm btn-light" >
              Confirm deal
            </button>
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
                <div class="mb-2" v-if="dealDetails.amount !== undefined">
                  <strong>Amount:</strong> ${{ dealDetails.amount.toFixed(2) }}
                </div>
                <div class="mb-2">
                  <strong>Status:</strong> <span class="badge" :class="getStatusBadgeClass()">{{ dealDetails.status }}</span>
                </div>
                <div class="mb-2">
                  <strong>Description:</strong> {{ dealDetails.description }}
                </div>
                <div class="mb-2" v-if="dealDetails.parties && dealDetails.parties.length">
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
import axios from 'axios';

// API configuration
const AUTH_API_URL = 'http://localhost:5001'; // Auth API URL (matches your Flask user.py)
const CHAT_API_URL = 'http://localhost:5040'; // Chat API URL (matches your Flask chat.py)

export default {
  name: 'ChatComponent',
  data() {
    return {
      isLoading: false,
      isChatLoading: false,
      apiError: null,
      
      // User data
      currentUserId: '',
      currentUserName: '',
      selectedChatUserId: null,
      selectedChatUser: null,
      chatUsers: [],
      
      // Messages
      messages: [],
      newMessage: "",
      validationError: "",
      
      // UI state
      showConfirmationModal: false,
      showReportModal: false,
      dealConfirmed: false,
      
      // Quick replies list for easier maintenance
      quickReplies: ["Let's do it", "Great!", "Sounds good"],
      
      // Deal details - if you're using deal functionality
      dealDetails: {
        id: "",
        name: "",
        date: "",
        amount: 0,
        status: "",
        description: "",
        parties: []
      },
      
      // Report data
      reportData: {
        type: "",
        description: ""
      }
    };
  },
  mounted() {
    // Check auth and initialize chats only when authenticated
    this.isLoading = true;
    this.checkAuth().then(isAuthenticated => {
      if (isAuthenticated) {
        // Only initialize data if authenticated
        this.initializeChats();
      } else {
        // If not authenticated, router guard should have redirected to login already
        console.log("Not authenticated, should redirect to login");
      }
    }).finally(() => {
      this.isLoading = false;
    });
  },
  methods: {
    // Navigation methods
    goBack() {
      if (window.history && window.history.length > 1) {
        this.$router.go(-1);
      } else {
        this.$router.push({ name: 'Home' });
      }
    },
    
    goToProfile() {
      this.$router.push({ name: 'Profile' });
    },
    
    // Authentication methods
      async checkAuth() {
      try {
        const response = await axios.get(`${AUTH_API_URL}/check-auth`, { 
          withCredentials: true 
        });
        
        if (response.data.code === 200 && response.data.data.authenticated) {
          this.currentUserId = response.data.data.uid;
          this.currentUserName = response.data.data.name;
          return true;
        } else {
          // Not authenticated, redirect to login
          console.log("Auth check failed in component - redirecting to login");
          this.$router.push('/login');
          return false;
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        this.$router.push('/login');
        return false;
      }
    },
    
    // Add this method to initialize chat data
    async initializeChats() {
      try {
        // Load users list
        await this.loadUsers();
      } catch (error) {
        console.error("Failed to initialize chats:", error);
        this.apiError = "Failed to load chat data. Please try again.";
      }
    },
    
    // Load users for chat sidebar
    async loadUsers() {
      try {
        this.isLoading = true;
        this.apiError = null;
        
        // Get all users from the user API
        const response = await axios.get(`${AUTH_API_URL}/user`, { 
          withCredentials: true 
        });
        
        if (response.data.code === 200) {
          // Filter out the current user
          const users = response.data.data.users.filter(user => user.uid !== this.currentUserId);
          
          // Transform to format needed for chat
          this.chatUsers = users.map(user => ({
            uid: user.uid,
            name: user.name,
            online: false, // You could implement online status if needed
            active: false,
            lastMessage: '',
            lastMessageTime: '',
            rating: user.rating
          }));
          
          // If we have users, select the first one
          if (this.chatUsers.length > 0) {
            this.selectChat(this.chatUsers[0].uid);
          }
        } else {
          console.error("Error loading users:", response.data ? response.data.message : "Unknown error");
          this.apiError = "Failed to load users list.";
        }
      } catch (error) {
        console.error("Error loading users:", error);
        this.apiError = "Failed to load users. Please try again later.";
      } finally {
        this.isLoading = false;
      }
    },
    
    // Select a chat
    selectChat(userId) {
      if (!userId) return;
      
      // Update the selected user
      this.selectedChatUserId = userId;
      
      // Find the user in our list
      const selectedUser = this.chatUsers.find(user => user.uid === userId);
      if (selectedUser) {
        this.selectedChatUser = selectedUser;
        
        // Update UI to show selected chat
        this.chatUsers.forEach(user => {
          user.active = user.uid === userId;
        });
        
        // Load chat messages for this user
        this.loadChatMessages(userId);
      }
    },
    
    // Load chat messages between current user and selected user
    async loadChatMessages(receiverId) {
      if (!this.currentUserId || !receiverId) return;
      
      try {
        this.isChatLoading = true;
        this.messages = []; // Clear previous messages
        let allMessages = [];
        
        try {
          // Get messages sent from current user to receiver
          const sentResponse = await axios.get(`${CHAT_API_URL}/chat/getmessagebetween/${this.currentUserId}/${receiverId}`);
          if (sentResponse.data.code === 200) {
            allMessages = [...sentResponse.data.data.messages];
          }
        } catch (error) {
          // Ignore 404 errors (no messages found)
          if (error.response && error.response.status !== 404) {
            throw error;
          }
        }
        
        try {
          // Get messages sent from receiver to current user
          const receivedResponse = await axios.get(`${CHAT_API_URL}/chat/getmessagebetween/${receiverId}/${this.currentUserId}`);
          if (receivedResponse.data.code === 200) {
            allMessages = [...allMessages, ...receivedResponse.data.data.messages];
          }
        } catch (error) {
          // Ignore 404 errors (no messages found)
          if (error.response && error.response.status !== 404) {
            throw error;
          }
        }
        
        if (allMessages.length > 0) {
          // Sort messages by timestamp
          this.messages = allMessages.sort((a, b) => {
            const dateA = new Date(a.sentat);
            const dateB = new Date(b.sentat);
            return dateA - dateB;
          });
          
          // Update last message in the sidebar
          const lastMsg = this.messages[this.messages.length - 1];
          const user = this.chatUsers.find(u => u.uid === receiverId);
          if (user) {
            user.lastMessage = lastMsg.message;
            user.lastMessageTime = this.formatTimeAgo(lastMsg.sentat);
          }
        }
      } catch (error) {
        console.error("Error loading chat messages:", error);
        this.apiError = "Failed to load messages. Please try again.";
      } finally {
        this.isChatLoading = false;
        // Scroll to bottom after messages are loaded
        this.$nextTick(() => {
          this.scrollToBottom();
        });
      }
    },
    
    // Send message methods
    async sendMessage() {
      // Validate message content
      if (!this.newMessage.trim()) {
        this.validationError = "Please enter a message";
        return;
      }
      
      // Clear validation error
      this.validationError = "";
      
      try {
        // Create timestamp for the message
        const timestamp = new Date().toISOString();
        
        // Send message to the server
        const response = await axios.post(`${CHAT_API_URL}/chat/send`, {
          senderid: this.currentUserId,
          receiverid: this.selectedChatUserId,
          message: this.newMessage,
          sentat: timestamp
        }, { withCredentials: true });
        
        if (response.data.code === 201) {
          // Add the new message to the chat
          this.messages.push(response.data.data.message);
          
          // Update last message in the sidebar
          const user = this.chatUsers.find(u => u.uid === this.selectedChatUserId);
          if (user) {
            user.lastMessage = this.newMessage;
            user.lastMessageTime = 'Just now';
          }
          
          // Clear input
          this.newMessage = "";
          
          // Scroll to bottom
          this.scrollToBottom();
        } else {
          this.validationError = "Failed to send message. Please try again.";
        }
      } catch (error) {
        console.error("Error sending message:", error);
        this.validationError = "Failed to send message. Please try again.";
      }
    },
    
    sendQuickReply(text) {
      // Set the text in the input field
      this.newMessage = text;
      // Send the message
      this.sendMessage();
    },
    
    // UI helper methods
    scrollToBottom() {
      this.$nextTick(() => {
        if (this.$refs.chatContent) {
          this.$refs.chatContent.scrollTop = this.$refs.chatContent.scrollHeight;
        }
      });
    },
    
    // Deal methods (if needed)
    showDealConfirmation() {
      this.showConfirmationModal = true;
    },
    
    closeModal() {
      this.showConfirmationModal = false;
    },
    
    confirmDeal() {
      // Implement your deal confirmation logic here
      this.dealDetails.status = "Confirmed";
      this.dealConfirmed = true;
      this.showConfirmationModal = false;
    },
    
    verifyDeal() {
      alert("Deal verification submitted!");
    },
    
    getStatusBadgeClass() {
      const statusMap = {
        "Confirmed": "bg-success",
        "Pending Confirmation": "bg-warning",
        "Rejected": "bg-danger",
        "Cancelled": "bg-secondary"
      };
      
      return statusMap[this.dealDetails.status] || "bg-primary";
    },
    
    // Report handling methods
    showReportDialog() {
      this.showReportModal = true;
      this.reportData = {
        type: "",
        description: ""
      };
    },
    
    submitReport() {
      if (!this.reportData.type || !this.reportData.description.trim()) {
        alert("Please fill in all report fields");
        return;
      }
      
      // Implement your report submission logic here
      this.showReportModal = false;
      alert("Your report has been submitted. Our team will review it shortly.");
    },
    
    // Utility methods
    formatMessageTime(timestamp) {
      if (!timestamp) return '';
      try {
        const date = new Date(timestamp);
        if (isNaN(date.getTime())) return ''; // Invalid date
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } catch (e) {
        console.error('Error formatting message time:', e);
        return '';
      }
    },
    
    formatShortTime(dateString) {
      if (!dateString) return '';
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return ''; // Invalid date
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } catch (e) {
        console.error('Error formatting short time:', e);
        return '';
      }
    },
     
    formatTimeAgo(timestamp) {
      if (!timestamp) return '';
      
      try {
        const date = new Date(timestamp);
        if (isNaN(date.getTime())) return '';
        
        const now = new Date();
        const diffMs = now - date;
        const diffSec = Math.floor(diffMs / 1000);
        
        if (diffSec < 60) return 'Just now';
        
        const diffMin = Math.floor(diffSec / 60);
        if (diffMin < 60) return `${diffMin}m ago`;
        
        const diffHour = Math.floor(diffMin / 60);
        if (diffHour < 24) return `${diffHour}h ago`;
        
        const diffDay = Math.floor(diffHour / 24);
        if (diffDay < 7) return `${diffDay}d ago`;
        
        return date.toLocaleDateString();
      } catch (e) {
        console.error('Error calculating time ago:', e);
        return '';
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