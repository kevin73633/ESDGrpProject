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
                  @click="selectChat(user.uid, user.dealid)"
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
                  <div class="bg-secondary rounded-circle" style="width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
                    <span class="text-white">{{ selectedChatUser ? selectedChatUser.name.charAt(0) : '?' }}</span>
                  </div>
                </div>
                <div>
                  <p class="fw-bold mb-0">{{ selectedChatUser ? selectedChatUser.name : 'No chat selected' }}</p>
                </div>
              </div>
              <div>
                <ReportButton 
                  v-if="canShowReportButton"
                  :reported-user-id="getOtherUserId()"
                  :current-user-id="currentUserId"
                  @report-submitted="handleReportSubmitted"
                  @show-notification="showNotification"
                />
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
            <div v-if="currentDeal && currentDeal.status==1" class="alert alert-success mb-3 d-flex align-items-center">
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
            <div class="card mb-3" v-if="currentDeal && currentDeal.id">
              <div class="card-body position-relative">
                <div class="d-flex align-items-center mb-3">
                  <div class="bg-light rounded-circle me-3 d-flex align-items-center justify-content-center" style="width: 40px; height: 40px;">
                    <span>{{ currentDeal.product ? currentDeal.product.title.charAt(0) : 'D' }}</span>
                  </div>
                  <div>
                    <p class="mb-0">{{ currentDeal.product ? currentDeal.product.title : 'Product' }}</p>
                    <p class="text-muted small mb-0">{{ currentDeal.createdAt ? formatDate(currentDeal.createdAt) : 'Unknown date' }}</p>
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
                      <p class="mb-0">{{ currentDeal.product ? currentDeal.product.title : 'Title' }}</p>
                      <p class="text-muted small mb-0">{{ currentDeal.product ? currentDeal.product.description : 'Description' }}</p>
                      <p v-if="currentDeal.product && currentDeal.product.price" class="text-primary fw-bold mb-0">
                        ${{ parseFloat(currentDeal.product.price).toFixed(2) }}
                      </p>
                    </div>
                    <div class="text-muted small">
                      {{ currentDeal.createdAt ? formatShortTime(currentDeal.createdAt) : '' }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Confirm/Verify Deal Button (if applicable) -->
            <div class="mb-4" v-if="dealDetails && dealDetails.id">
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
            <!-- Deal button: Confirm or Verify based on status -->
            <div v-if="currentDeal" class="mb-3">
              <!-- Show ConfirmDealButton if deal is in pending status -->
              <ConfirmDealButton 
                v-if="canConfirmDeal"
                :deal-id="currentDeal.id"
                :product-id="currentDeal.product ? currentDeal.product.id : ''"
                :user-id="currentUserId"
                :price="currentDeal.product.price"
                @deal-confirmed="handleDealConfirmed"
                @show-notification="showNotification"
              />
              <!-- Show Verify Deal button if deal is already confirmed -->
              <VerifyButton 
              v-if="canVerifyReceipt"
              :deal-id="currentDeal.id"
              :product-id="currentDeal.product ? currentDeal.product.id : ''"
              :user-id="currentUserId"
              :price="currentDeal.product ? currentDeal.product.price : 0"
              @deal-verified="handleDealVerified"
              @show-notification="showNotification"
              />
            </div>
            
            <!-- Message input form -->
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
    
    <!-- Notification component -->
    <div v-if="notification" :class="['notification', notification.type]">
      {{ notification.message }}
      <button @click="notification = null" class="close-notification">&times;</button>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import ConfirmDealButton from '../components/ConfirmDealButton.vue';
import ReportButton from '../components/ReportButton.vue';
import VerifyButton from '../components/VerifyButton.vue';

// API configuration
const AUTH_API_URL = 'http://localhost:5001'; // Auth API URL (matches your Flask user.py)
const CHAT_API_URL = 'http://localhost:5087'; // Chat API URL (matches your Flask chat.py)
const DEAL_API_URL = 'http://localhost:5020'; // Chat API URL (matches your Flask chat.py)
const PRODUCT_API_URL = 'http://localhost:5005'; // Product API URL

export default {
  name: 'ChatComponent',
  components: {
    ConfirmDealButton,
    ReportButton,
    VerifyButton
  },
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

      // Deal data
      currentDeal: null,
      selectedDealId: null,
      
      // UI state
      notification: null,

      dealDetails: {
        id: null,
        name: '',
        date: '',
        amount: 0,
        status: 0,
        description: '',
        parties: []
      },
      verificationStatus: {
        buyerVerified: false,
        sellerVerified: false
      },
      
      // Quick replies list for easier maintenance
      quickReplies: ["Let's do it", "Great!", "Sounds good"],
    };
  },
  computed: {
    // Only show confirm deal button if user is buyer and deal is in pending status
    canConfirmDeal() {
      return this.currentDeal && 
             (this.currentUserId == this.currentDeal.buyerId && (this.currentDeal.status == 0 || this.currentDeal.status == 2) || 
             this.currentUserId == this.currentDeal.sellerId && (this.currentDeal.status == 0 || this.currentDeal.status == 1))
    },

    canVerifyReceipt() {
      if (!this.currentDeal) return false;
      
      const isValidStatus = this.currentDeal.status === 3 || this.currentDeal.status === 4;
      
      // Check if the current user has already verified
      let currentUserVerified = false;
      if (this.currentUserId === this.currentDeal.buyerId) {
        currentUserVerified = this.verificationStatus.buyerVerified;
      } else if (this.currentUserId === this.currentDeal.sellerId) {
        currentUserVerified = this.verificationStatus.sellerVerified;
      }
      
      return isValidStatus && !currentUserVerified;
    },
    
    // Determine if we can show the report button
    canShowReportButton() {
      return this.selectedChatUserId && this.currentUserId && this.selectedChatUserId !== this.currentUserId;
    }
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
    
    // Initialize chat data
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
    
    // Get all deals for the current user
    this.chatUsers = [];
    
    console.log("Fetching deals for user:", this.currentUserId);
    const dealsResponse = await axios.get(`${DEAL_API_URL}/get_deals_with_user/${this.currentUserId}`);
    
    // Log the deals response for debugging
    console.log("Deals response:", dealsResponse.data);
    
    if (dealsResponse.data.code === 200 && dealsResponse.data.data && dealsResponse.data.data.deals) {
      const deals = dealsResponse.data.data.deals;
      console.log(`Found ${deals.length} deals`);
      
      // For each deal, get the other user's information
      for (let deal of deals) {
        // Determine the other user ID (seller or buyer)
        const otherUserId = (this.currentUserId == deal.sellerid) 
          ? deal.buyerid 
          : deal.sellerid;
        
        console.log(`Processing deal ${deal.dealid} with other user ${otherUserId}`);
        
        try {
          console.log(`Fetching user data for ID: ${otherUserId}`);
          const userResponse = await axios.get(`${AUTH_API_URL}/user/${otherUserId}`, { 
            withCredentials: true 
          });
          
          // Log the complete user response for debugging
          console.log(`User API response for ${otherUserId}:`, userResponse.data);
          
          // Create a placeholder user if we can't get real data
          let userData = {
            uid: otherUserId,
            name: `User ${otherUserId.substring(0, 4)}...`,
            online: false,
            rating: 0
          };
          
          // Try to extract actual user data if available
          if (userResponse.data.code === 200 && userResponse.data.data) {
            // Check different possible structures
            if (userResponse.data.data.user) {
              if (Array.isArray(userResponse.data.data.user) && userResponse.data.data.user.length > 0) {
                // If it's an array, use the first item
                const user = userResponse.data.data.user[0];
                if (user && user.uid) {
                  userData = {
                    uid: user.uid,
                    name: user.name || `User ${user.uid.substring(0, 4)}...`,
                    online: false,
                    rating: user.rating || 0
                  };
                }
              } else if (userResponse.data.data.user.uid) {
                // If it's a direct object
                const user = userResponse.data.data.user;
                userData = {
                  uid: user.uid,
                  name: user.name || `User ${user.uid.substring(0, 4)}...`,
                  online: false,
                  rating: user.rating || 0
                };
              }
            }
          }
          
          // Add to chat users with fallback data if needed
          this.chatUsers.push({
            uid: userData.uid,
            name: userData.name,
            online: userData.online,
            active: false,
            lastMessage: '',
            lastMessageTime: '',
            rating: userData.rating,
            dealid: deal.dealid
          });
          
          console.log(`Added user to chat list: ${userData.name} (${userData.uid})`);
          
        } catch (userError) {
          console.error(`Error fetching user ${otherUserId}:`, userError);
          
          // Still add user with minimal data since we know they exist
          this.chatUsers.push({
            uid: otherUserId,
            name: `User ${otherUserId.substring(0, 4)}...`, // Show partial ID as name
            online: false,
            active: false,
            lastMessage: '',
            lastMessageTime: '',
            rating: 0,
            dealid: deal.dealid
          });
          
          console.log(`Added placeholder user for ID ${otherUserId}`);
        }
      }
      
      console.log(`Final chat users count: ${this.chatUsers.length}`);
    } else {
      console.error("Invalid deals response format:", dealsResponse.data);
      this.apiError = "Failed to load deals. Invalid response format.";
    }
    
    // If we have users, select the first one
    if (this.chatUsers.length > 0) {
      console.log("Selecting first chat user:", this.chatUsers[0]);
      this.selectChat(this.chatUsers[0].uid, this.chatUsers[0].dealid);
    } else {
      console.log("No chat users found");
      this.selectedChatUser = null;
      this.selectedChatUserId = null;
      this.selectedDealId = null;
      this.messages = [];
      this.currentDeal = null;
    }
  } catch (error) {
    console.error("Error loading users:", error);
    this.apiError = "Failed to load users. Please try again later.";
  } finally {
    this.isLoading = false;
  }
},
    
    // Select a chat
    selectChat(userId, dealId) {
      if (!userId) return;
      
      // Update the selected user
      this.selectedChatUserId = userId;
      this.selectedDealId = dealId;
      
      // Find the user in our list
      const selectedUser = this.chatUsers.find(user => user.dealid === dealId);
      if (selectedUser) {
        this.selectedChatUser = selectedUser;
        
        // Update UI to show selected chat
        this.chatUsers.forEach(user => {
          user.active = user.uid === userId;
        });
        
        // Load chat messages for this user
        this.loadChatMessages(dealId);

        if (dealId) {
          this.loadDealInformation(dealId);
        } else {
          this.currentDeal = null;
        }
      }
    },

    // Load deal information
    async loadDealInformation(dealId) {
      if (!dealId) return;
      
      try {
        // Get deal information
        const dealResponse = await axios.get(`${DEAL_API_URL}/deal/${dealId}`);
        
        if (dealResponse.data.code === 200 && dealResponse.data.data.deal) {
          const dealData = dealResponse.data.data.deal;
          
          // Get product details
          const productResponse = await axios.get(`${PRODUCT_API_URL}/products/${dealData.productid}`);
          
          if (productResponse.data.code === 200 && productResponse.data.data.product) {
            const productData = productResponse.data.data.product;
            
            // Save combined deal and product information
            this.currentDeal = {
              id: dealData.dealid,
              buyerId: dealData.buyerid,
              sellerId: dealData.sellerid,
              status: dealData.status,
              createdAt: dealData.createdat,
              product: {
                id: productData.productid,
                title: productData.title,
                price: productData.price,
                description: productData.description || 'No description available',
                imageUrl: productData.image_url || null
              }
            };
          } else {
            // Deal exists but product details couldn't be fetched
            this.currentDeal = {
              id: dealData.dealid,
              buyerId: dealData.buyerid,
              sellerId: dealData.sellerid,
              status: dealData.status,
              createdAt: dealData.createdat,
              product: {
                id: dealData.productid,
                title: 'Unknown Product',
                price: 0,
                description: 'Product details unavailable'
              }
            };
          }
        } else {
          this.currentDeal = null;
        }
      } catch (error) {
        console.error("Error loading deal information:", error);
        this.showNotification({
          message: "Failed to load deal information",
          type: "error"
        });
        this.currentDeal = null;
      }
    },
    
    // Load chat messages between current user and selected user
    async loadChatMessages(dealid) {
      if (!dealid) return;
      
      try {
        this.isChatLoading = true;
        this.messages = []; // Clear previous messages
        let allMessages = [];
        
        try {
          // Get messages sent from current user to receiver
          const sentResponse = await axios.get(`${CHAT_API_URL}/chat/getmessagebetween/${dealid}`);
          if (sentResponse.data.code === 200) {
            allMessages = [...sentResponse.data.data.messages];
          }
        } catch (error) {
          // Ignore 404 errors (no messages found)
          if (error.response && error.response.status !== 404) {
            throw error;
          }
        }
        
        // try {
        //   // Get messages sent from receiver to current user
        //   const receivedResponse = await axios.get(`${CHAT_API_URL}/chat/getmessagebetween/${dealid}`);
        //   if (receivedResponse.data.code === 200) {
        //     allMessages = [...allMessages, ...receivedResponse.data.data.messages];
        //   }
        // } catch (error) {
        //   // Ignore 404 errors (no messages found)
        //   if (error.response && error.response.status !== 404) {
        //     throw error;
        //   }
        // }
        
        if (allMessages.length > 0) {
          // Sort messages by timestamp
          this.messages = allMessages.sort((a, b) => {
            const dateA = new Date(a.sentat);
            const dateB = new Date(b.sentat);
            return dateA - dateB;
          });
          
          // Update last message in the sidebar
          const lastMsg = this.messages[this.messages.length - 1];
          const user = this.chatUsers.find(u => u.dealid === dealid);
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
          dealid: this.selectedDealId,
          message: this.newMessage,
          sentat: timestamp
        }, { withCredentials: true });
        
        if (response.data.code === 201) {
          // Add the new message to the chat
          this.messages.push(response.data.data.message);
          
          // Update last message in the sidebar
          const user = this.chatUsers.find(u => u.dealid === this.selectedDealId);
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

    // Helper to get the other user's ID for the report button
    getOtherUserId() {
      return this.selectedChatUserId || "";
    },

    // Handle deal confirmation result
    handleDealConfirmed(result) {
      console.log("Deal confirmed:", result);
      
      // Update current deal status to confirmed
      if (this.currentDeal) {
        if (this.currentDeal.status ==0){
          this.currentDeal.status = 1;
        }
        else{
          this.currentDeal.status = 2;
        }
      }
      
      // Show success notification
      this.showNotification({
        message: `Deal for ${result.product.title} has been confirmed successfully!`,
        type: 'success'
      });
      
      // Refresh deal information
      this.loadDealInformation(this.selectedDealId);
      
      // Scroll to top to show the banner
      if (this.$refs.chatContent) {
        this.$refs.chatContent.scrollTop = 0;
      }
    },

    // Handle deal verified result
    handleDealVerified(data) {
      console.log("Deal verified:", data);
      
      // Update current deal status to verified
      if (this.currentDeal) {
        this.currentDeal.status = 3;
      }
      
      // Show success notification
      this.showNotification({
        message: `Receipt of goods for ${data.product.title} has been verified successfully!`,
        type: 'success'
      });
      
      // Refresh deal information
      this.loadDealInformation(this.selectedDealId);
      
      // Scroll to top to show the banner
      if (this.$refs.chatContent) {
        this.$refs.chatContent.scrollTop = 0;
      }
    },
    
    // Handle report submission
    handleReportSubmitted(result) {
      console.log("Report submitted:", result);
      
      // Show notification instead of adding system message
      this.showNotification({
        message: "Your report has been submitted and is under review by our team.",
        type: "info"
      });
    },
    
    // Show notification
    showNotification({ message, type }) {
      this.notification = { message, type };
      
      // Auto-hide notification after 5 seconds
      setTimeout(() => {
        if (this.notification && this.notification.message === message) {
          this.notification = null;
        }
      }, 5000);
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
      this.dealDetails.status = 1;
      this.dealConfirmed = true;
      this.showConfirmationModal = false;
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
    formatDate(dateString) {
      if (!dateString) return '';
      
      try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) return ''; // Invalid date
        return date.toLocaleDateString(undefined, { 
          year: 'numeric', 
          month: 'short', 
          day: 'numeric'
        });
      } catch (e) {
        console.error('Error formatting date:', e);
        return '';
      }
    },

    formatMessageTime(timestamp) {
      if (!timestamp) return '';
      
      try {
        const date = new Date(timestamp);
        if (isNaN(date.getTime())) return '';
        
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } catch (e) {
        console.error('Error formatting message time:', e);
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