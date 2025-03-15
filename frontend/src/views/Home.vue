<template>
  <div class="home">
    <!-- Navbar (Top) -->
    <nav class="navbar navbar-light bg-light">
      <div class="container-fluid">
        <input v-model="searchQuery" type="search" class="form-control" placeholder="Search for deals..." aria-label="Search">
      </div>
    </nav>
    
    <!-- Categories Section -->
    <section class="categories">
      <h5 class="mt-3">Categories</h5>
      <div class="category-list">
        <button class="category-item" v-for="category in categories" :key="category">{{ category }}</button>
      </div>
    </section>

    <!-- Featured Deals -->
    <section class="featured-deals mt-4">
      <h5>Featured Deals</h5>
      <div class="deal-list">
        <div class="deal-item" v-for="deal in deals" :key="deal.id">
          <img :src="deal.image" alt="deal-image" class="deal-image">
          <div class="deal-info">
            <h6>{{ deal.title }}</h6>
            <span class="badge rounded-pill text-bg-light">{{ deal.category }}</span>
            <p>{{ deal.description }}</p>
            <button class="btn btn-primary">View Deal</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Post Deal Button (Floating) -->
    <button class="btn btn-primary post-deal-btn" @click="openModal">Post a Deal</button>

    <!-- Modal for Posting a Deal -->
    <div class="modal fade" id="dealModal" tabindex="-1" aria-labelledby="dealModalLabel" aria-hidden="true" ref="dealModal">
      <div class="modal-dialog modal-dialog-centered"> 
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="dealModalLabel">Post a New Deal</h5>
            <button type="button" class="btn-close" @click="closeModal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitDeal">
              <div class="mb-3">
                <label for="dealTitle" class="form-label">Deal Title</label>
                <input type="text" class="form-control" v-model="newDeal.title" id="dealTitle" required />
              </div>
              <div class="mb-3">
                <label for="dealCategory" class="form-label">Category</label>
                <select class="form-select" v-model="newDeal.category" id="dealCategory" required>
                  <option value="food">Food</option>
                  <option value="electronics">Electronics</option>
                  <option value="fashion">Fashion</option>
                  <option value="books">Books</option>
                </select>
              </div>
              <div class="mb-3">
                <label for="dealDescription" class="form-label">Description</label>
                <textarea class="form-control" v-model="newDeal.description" id="dealDescription" rows="3" required></textarea>
              </div>
              <div class="modal-footer">
                <button type="submit" class="btn btn-primary">Submit Deal</button>
                <button type="button" class="btn btn-secondary" @click="closeModal">Close</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>  

  </div>

</template>

<script>
import { Modal } from 'bootstrap'; // Import Bootstrap Modal

export default {
  data() {
    return {
      searchQuery: "",
      categories: ["Electronics", "Fashion", "Food", "Services", "Books", "Furniture"],
      deals: [
        { id: 1, title: "1-for-1 Bubble Tea", category: "food", description: "Looking for someone to share a bubble tea deal.", image: "path-to-image.jpg" },
        { id: 2, title: "Donut Box for $15", category: "food", description: "Need someone to share a box of donuts.", image: "path-to-image.jpg" },
      ],
      newDeal: {
        title: "",
        category: "food",
        description: "",
      },
    };
  },
  methods: {
    openModal() {
      if (this.$refs.dealModal) {
        const modalElement = this.$refs.dealModal;
        const modalInstance = new Modal(modalElement); 
        modalInstance.show();
        this.modalInstance = modalInstance; 
      }
    },
    closeModal() {
      if (this.modalInstance) {
        this.modalInstance.hide();
      }
    }
  }
};
</script>


<style scoped>
.home {
  padding: 10px;
}

.navbar {
  background-color: #fff;
}

.categories {
  padding: 10px;
}

.category-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
}

.category-item {
  padding: 10px 20px;
  background-color: #f7f7f7;
  border: 1px solid #ddd;
  border-radius: 5px;
}

.featured-deals {
  padding: 10px;
}

.deal-list {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.deal-item {
  border: 1px solid #ddd;
  border-radius: 5px;
  padding: 10px;
}

.deal-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.post-deal-btn {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 10;
}
</style>
