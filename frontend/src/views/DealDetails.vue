<template>
    <div>
      <h1>{{ deal.title }}</h1>
      <p>{{ deal.description }}</p>
      <p><strong>Price:</strong> {{ deal.price }}</p>
      <router-link :to="{ name: 'Chat', params: { dealId: deal.id } }">Chat with Seller</router-link>
    </div>
  </template>
  
  <script>
  export default {
    props: ['id'],
    data() {
      return {
        deal: {
          id: this.id,
          title: '1 for 1 Bubble Tea',
          category: 'food',
          description: 'Looking for someone to share a bubble tea deal with.',
          price: '$5.00',
        },
      };
    },
  };
  </script>
  