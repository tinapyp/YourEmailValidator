<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>YourEmailValidator - Simple Email Validation API</title>
    <link
      href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"
      rel="stylesheet"
    />
    <style>
      @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap");
      body {
        font-family: "Inter", sans-serif;
      }
      .bg-gradient {
        background: linear-gradient(to bottom, #ffffff, #f9fafb);
      }
      .text-gradient {
        background: linear-gradient(to right, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
      }
      .btn-gradient {
        background: linear-gradient(to right, #8b5cf6, #ec4899);
      }
      .card-hover:hover {
        box-shadow: 0 10px 15px -3px rgba(139, 92, 246, 0.1),
          0 4px 6px -2px rgba(236, 72, 153, 0.05);
      }

      #faq details {
        border-bottom: 1px solid #e5e7eb;
      }


      @keyframes pulse-border {
        0%, 100% { 
          border-color: var(--pulse-color, #9a58df);
          box-shadow: 0 0 15px 10px var(--pulse-color, #9a58df);
        }
        50% { 
          border-color: transparent;
          box-shadow: 0 0 30px 10px transparent;
        }
      }
    
      /* Apply pulse animation to the button */
      .pulse-border-animation {
        border: 2px solid var(--pulse-color, #9a58df);
        border-radius: 9999px; /* Full-rounded corners */
        animation: pulse-border var(--duration, 1.5s) infinite;
      }
    </style>
  </head>
  <body class="bg-gradient min-h-screen flex flex-col">
    <header
      class="px-4 lg:px-6 h-14 flex items-center backdrop-filter backdrop-blur-sm bg-white bg-opacity-50 sticky top-0 z-50"
    >
      <a href="#" class="flex items-center justify-center">
        <i class="h-6 w-6 text-purple-500"></i>
        <span class="ml-2 text-lg font-bold"
          >YourEmailValidator</span
        >
      </a>
      <nav class="ml-auto flex gap-4 sm:gap-6">
        <a
          href="#features"
          class="text-sm font-medium hover:text-purple-500 transition-colors"
          >Features</a
        >
        <a
          href="#pricing"
          class="text-sm font-medium hover:text-purple-500 transition-colors"
          >Pricing</a
        >
        <a
          href="#faq"
          class="text-sm font-medium hover:text-purple-500 transition-colors"
          >FAQ</a
        >
      </nav>
    </header>

    <main class="flex-1">
      <section class="w-full py-12 md:py-24 lg:py-32 xl:py-48">
        <div class="container px-4 md:px-6 mx-auto">
          <div class="flex flex-col items-center space-y-4 text-center">
            <h1
              class="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl text-gradient"
            >
              Validate emails with confidence ✨
            </h1>
            <p
              class="mx-auto max-w-[700px] text-gray-500 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed"
            >
              Simple, reliable email validation API for developers. Prevent fake
              signups and maintain a clean email list.
            </p>
            <div class="space-x-4">
              <a
                href="#"
                class="inline-flex items-center justify-center px-8 py-3 text-base font-medium text-white bg-purple-500 hover:bg-purple-600 rounded-full shadow-lg shadow-purple-500/25"
              >
                Get Started Free
              </a>
              <a
                href="#"
                class="inline-flex items-center justify-center px-8 py-3 text-base font-medium text-gray-900 bg-white border border-gray-200 rounded-full hover:bg-gray-50"
              >
                View on GitHub
              </a>
            </div>
          </div>
        </div>
      </section>
      

      <section id="features" class="w-full py-12 md:py-24 lg:py-32">
        <div class="container px-4 md:px-6 mx-auto">
          <div
            class="flex flex-col items-center justify-center space-y-4 text-center mb-12"
          >
            <h2
              class="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl"
            >
              Experience improved <span class="text-gradient">validation</span>
            </h2>
            <p class="max-w-[600px] text-gray-500 md:text-xl/relaxed">
              Powerful features to make your email validation process seamless
              and efficient
            </p>
          </div>
          <div class="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <div
              class="relative overflow-hidden group bg-white p-6 rounded-lg shadow-md card-hover"
            >
              <div
                class="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
              ></div>
              <i data-lucide="zap" class="w-10 h-10 text-purple-500 mb-4"></i>
              <h3 class="text-xl font-semibold mb-2">Real-time Validation</h3>
              <p class="text-gray-500">
                Instant validation results with detailed response codes
              </p>
            </div>
            <div
              class="relative overflow-hidden group bg-white p-6 rounded-lg shadow-md card-hover"
            >
              <div
                class="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
              ></div>
              <i
                data-lucide="database"
                class="w-10 h-10 text-purple-500 mb-4"
              ></i>
              <h3 class="text-xl font-semibold mb-2">Bulk Validation</h3>
              <p class="text-gray-500">
                Process multiple email addresses in a single API call
              </p>
            </div>
            <div
              class="relative overflow-hidden group bg-white p-6 rounded-lg shadow-md card-hover"
            >
              <div
                class="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity"
              ></div>
              <i
                data-lucide="shield"
                class="w-10 h-10 text-purple-500 mb-4"
              ></i>
              <h3 class="text-xl font-semibold mb-2">Open Source</h3>
              <p class="text-gray-500">
                Self-host our solution or contribute to the codebase
              </p>
            </div>
          </div>
        </div>
      </section>

      <section class="text-center mb-8">
        <a
          href="#"
          style="--pulse-color:#9a58df; --duration:1.5s;"
          class="inline-flex items-center justify-center px-8 py-3 text-base font-medium text-white bg-purple-500 hover:bg-purple-600 rounded-full shadow-lg shadow-purple-500/25 pulse-border-animation"
        >
          Support Us
        </a>
        <p style="margin-top: 15px;">Build your email list with confidence</p>
      </section>

      <section id="pricing" class="w-full py-12 md:py-24 lg:py-32 relative">
        <div
          class="absolute inset-0 bg-gradient-to-b from-purple-500/5 to-transparent"
        ></div>
          <div
            class="flex flex-col items-center justify-center space-y-4 text-center mb-12"
          >
            <h2
              class="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl text-gradient"
            >
              Simple pricing for everyone
            </h2>
            <p class="max-w-[600px] text-gray-500 md:text-xl/relaxed">
              Choose the perfect plan for your needs
            </p>
          </div>
          <div class="grid gap-8 md:grid-cols-2 max-w-5xl mx-auto">
            <div
              class="relative group bg-white p-6 rounded-lg shadow-md card-hover"
            >
              <div
                class="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg"
              ></div>
              <h3 class="text-2xl font-semibold mb-2 flex items-center gap-2">
                Free Tier
                <span
                  class="inline-block px-3 py-1 text-xs bg-purple-100 text-purple-500 rounded-full"
                >
                  Popular
                </span>
              </h3>
              <div class="text-5xl font-bold mb-4">$0</div>
              <p class="text-gray-500 mb-6">Perfect for small projects</p>
              <ul class="space-y-4 mb-6">
                <li class="flex items-center gap-3">
                  <i data-lucide="check" class="w-5 h-5 text-purple-500"></i>
                  <span>100 API calls per month</span>
                </li>
                <li class="flex items-center gap-3">
                  <i data-lucide="check" class="w-5 h-5 text-purple-500"></i>
                  <span>Basic email validation</span>
                </li>
              </ul>
              <a
                href="#"
                class="block w-full py-3 px-4 text-center text-white bg-purple-500 hover:bg-purple-600 rounded-full font-medium"
              >
                Get Started
              </a>
            </div>
            <div
              class="relative group bg-white p-6 rounded-lg shadow-md card-hover border-2 border-purple-500"
            >
              <div
                class="absolute inset-0 bg-gradient-to-r from-purple-500/10 to-pink-500/10 opacity-0 group-hover:opacity-100 transition-opacity rounded-lg"
              ></div>
              <h3 class="text-2xl font-semibold mb-2 flex items-center gap-2">
                Donatur Tier
                <span
                  class="inline-block px-3 py-1 text-xs text-white bg-gradient-to-r from-purple-500 to-pink-500 rounded-full"
                >
                  Unlimited
                </span>
              </h3>
              <div class="text-5xl font-bold mb-4 text-gradient">Custom</div>
              <p class="text-gray-500 mb-6">For power users</p>
              <ul class="space-y-4 mb-6">
                <li class="flex items-center gap-3">
                  <i data-lucide="check" class="w-5 h-5 text-purple-500"></i>
                  <span>Unlimited API calls</span>
                </li>
                <li class="flex items-center gap-3">
                  <i data-lucide="check" class="w-5 h-5 text-purple-500"></i>
                  <span>Bulk validation support</span>
                </li>
              </ul>
              <a
                href="#"
                class="block w-full py-3 px-4 text-center text-white btn-gradient hover:opacity-90 rounded-full font-medium"
              >
                Donate
              </a>
            </div>
          </div>
        </div>
      </section>

      <section id="faq" class="w-full py-12 md:py-24 bg-gray-200">
        <div class="container max-w-4xl mx-auto px-4 md:px-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
            <div class="space-y-2 text-center md:text-left">
              <h3 class="text-sm font-medium leading-none text-muted-foreground">FAQ</h3>
              <h2 class="text-3xl font-bold tracking-tight">Frequently Asked Questions</h2>
            </div>
            <div class="space-y-4">
              <!-- FAQ Item 1 -->
              <div class="border-b border-gray-200">
                <button class="flex justify-between items-center w-full py-4 text-left toggle-faq">
                  <span class="font-medium">Is the API rate-limited?</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
                    <path d="M12 5v14M5 12h14"></path>
                  </svg>
                </button>
                <div class="pb-4 text-muted-foreground faq-content hidden">
                  Yes, the free tier is limited to 100 API calls per month. The Donatur tier offers unlimited API calls.
                </div>
              </div>
              <!-- FAQ Item 2 -->
              <div class="border-b border-gray-200">
                <button class="flex justify-between items-center w-full py-4 text-left toggle-faq">
                  <span class="font-medium">Can I self-host the API?</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
                    <path d="M12 5v14M5 12h14"></path>
                  </svg>
                </button>
                <div class="pb-4 text-muted-foreground faq-content hidden">
                  Yes! Our API is open-source and available on GitHub. You can self-host it on your own infrastructure.
                </div>
              </div>
              <!-- FAQ Item 3 -->
              <div class="border-b border-gray-200">
                <button class="flex justify-between items-center w-full py-4 text-left toggle-faq">
                  <span class="font-medium">What validation methods are used?</span>
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-5 h-5">
                    <path d="M12 5v14M5 12h14"></path>
                  </svg>
                </button>
                <div class="pb-4 text-muted-foreground faq-content hidden">
                  We use multiple validation methods including syntax checking, domain validation, and MX record verification.
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

    </main>

    <script src="https://unpkg.com/lucide@latest"></script>
    <script>
      lucide.createIcons();
      
      document.querySelectorAll('.toggle-faq').forEach(button => {
        button.addEventListener('click', () => {
          const content = button.nextElementSibling;
          content.classList.toggle('hidden');
        });
      });
    </script>
  </body>
</html>
